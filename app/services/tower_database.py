import httpx
from typing import Optional, Tuple, Dict, List
from datetime import datetime
from app.database import mongodb, redis_client
from app.config import settings
from app.models.schemas import CellTowerData
import logging
import json

logger = logging.getLogger(__name__)

class TowerDatabase:
    """Manages cell tower location database with OpenCellID integration"""
    
    def __init__(self):
        self.opencellid_url = "https://opencellid.org/cell/get"
        self.cache = {}
    
    async def get_tower_location(
        self,
        cid: int,
        lac: int,
        mcc: int,
        mnc: int
    ) -> Optional[Tuple[float, float]]:
        """
        Get tower location (lat, lon) with caching
        Priority: Redis -> Local Cache -> MongoDB -> OpenCellID
        """
        
        cache_key = f"tower:{mcc}:{mnc}:{lac}:{cid}"
        
        # 1. Check Redis cache
        if redis_client.client:
            try:
                cached = await redis_client.client.get(cache_key)
                if cached:
                    data = json.loads(cached)
                    return (data['lat'], data['lon'])
            except Exception as e:
                logger.debug(f"Redis cache miss: {e}")
        
        # 2. Check local cache
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # 3. Check MongoDB
        tower = await mongodb.db.towers.find_one({
            "cid": cid,
            "lac": lac,
            "mcc": mcc,
            "mnc": mnc
        })
        
        if tower and 'location' in tower:
            coords = tower['location']['coordinates']
            location = (coords[1], coords[0])  # (lat, lon)
            
            # Cache it
            self.cache[cache_key] = location
            if redis_client.client:
                try:
                    await redis_client.client.setex(
                        cache_key,
                        86400,  # 24 hours
                        json.dumps({'lat': location[0], 'lon': location[1]})
                    )
                except Exception as e:
                    logger.debug(f"Redis cache set error: {e}")
            
            return location
        
        # 4. Query OpenCellID (if API key available)
        if settings.OPENCELLID_API_KEY:
            location = await self.query_opencellid(cid, lac, mcc, mnc)
            if location:
                # Save to MongoDB
                await self.save_tower(cid, lac, mcc, mnc, location[0], location[1])
                
                # Cache it
                self.cache[cache_key] = location
                if redis_client.client:
                    try:
                        await redis_client.client.setex(
                            cache_key,
                            86400,
                            json.dumps({'lat': location[0], 'lon': location[1]})
                        )
                    except Exception as e:
                        logger.debug(f"Redis cache set error: {e}")
                
                return location
        
        # 5. Use mock tower data for demo (Knowledge Park)
        return await self.get_mock_tower_location(cid)
    
    async def query_opencellid(
        self,
        cid: int,
        lac: int,
        mcc: int,
        mnc: int
    ) -> Optional[Tuple[float, float]]:
        """Query OpenCellID API for tower location"""
        
        try:
            async with httpx.AsyncClient() as client:
                params = {
                    "key": settings.OPENCELLID_API_KEY,
                    "mcc": mcc,
                    "mnc": mnc,
                    "lac": lac,
                    "cellid": cid,
                    "format": "json"
                }
                
                response = await client.get(self.opencellid_url, params=params, timeout=5.0)
                
                if response.status_code == 200:
                    data = response.json()
                    if 'lat' in data and 'lon' in data:
                        return (float(data['lat']), float(data['lon']))
        
        except Exception as e:
            logger.warning(f"OpenCellID query failed: {e}")
        
        return None
    
    async def save_tower(
        self,
        cid: int,
        lac: int,
        mcc: int,
        mnc: int,
        lat: float,
        lon: float
    ):
        """Save tower location to MongoDB"""
        
        try:
            tower_doc = {
                "cid": cid,
                "lac": lac,
                "mcc": mcc,
                "mnc": mnc,
                "location": {
                    "type": "Point",
                    "coordinates": [lon, lat]  # GeoJSON: [lon, lat]
                },
                "updated_at": datetime.utcnow()
            }
            
            await mongodb.db.towers.update_one(
                {"cid": cid, "lac": lac, "mcc": mcc, "mnc": mnc},
                {"$set": tower_doc},
                upsert=True
            )
            
            logger.info(f"Saved tower: CID={cid}, LAC={lac}")
            
        except Exception as e:
            logger.error(f"Error saving tower: {e}")
    
    async def get_mock_tower_location(self, cid: int) -> Optional[Tuple[float, float]]:
        """Get mock tower locations for demo mode (Knowledge Park)"""
        
        # Mock towers for Knowledge Park, Greater Noida
        mock_towers = {
            12345: (28.4720, 77.4880),  # Tower KP1-A
            12346: (28.4690, 77.4960),  # Tower KP2-A
            12347: (28.4640, 77.5050),  # Tower KP3-A
            12348: (28.4710, 77.5000),  # Tower Alpha-A
        }
        
        if cid in mock_towers:
            location = mock_towers[cid]
            # Save to database for consistency
            await self.save_tower(cid, 101, 404, 45, location[0], location[1])
            return location
        
        return None
    
    async def get_tower_locations_bulk(
        self,
        cells: List[CellTowerData]
    ) -> Dict[int, Tuple[float, float]]:
        """Get locations for multiple towers at once"""
        
        locations = {}
        
        for cell in cells:
            location = await self.get_tower_location(
                cell.cid,
                cell.lac,
                cell.mcc,
                cell.mnc
            )
            if location:
                locations[cell.cid] = location
        
        return locations

# Global instance
tower_db = TowerDatabase()
