"""
OpenCellID API Integration
Fetches real cell tower locations for positioning calculations
"""
import httpx
import logging
from typing import Optional, Dict, Any
from app.database import mongodb

logger = logging.getLogger(__name__)

OPENCELLID_API_KEY = "pk.6f1b2fb9578529b4d78d5b5912b99e2b"
OPENCELLID_BASE_URL = "https://opencellid.org/cell/get"

class OpenCellIDService:
    """Service to query OpenCellID for tower locations"""
    
    def __init__(self):
        self.api_key = OPENCELLID_API_KEY
        self.cache_collection = mongodb.db.towers if mongodb.db else None
    
    async def get_tower_location(
        self, 
        mcc: int, 
        mnc: int, 
        lac: int, 
        cid: int
    ) -> Optional[Dict[str, Any]]:
        """
        Get tower location from OpenCellID or local cache
        
        Args:
            mcc: Mobile Country Code (404 for India)
            mnc: Mobile Network Code (45 for Airtel, 40 for Jio, etc)
            lac: Location Area Code
            cid: Cell ID
        
        Returns:
            Tower data with lat, lon, range, etc. or None if not found
        """
        try:
            # Check local cache first
            cached_tower = await self.get_cached_tower(mcc, mnc, lac, cid)
            if cached_tower:
                logger.info(f"Tower {cid} found in cache")
                return cached_tower
            
            # Query OpenCellID API
            logger.info(f"Querying OpenCellID for tower: MCC={mcc}, MNC={mnc}, LAC={lac}, CID={cid}")
            tower_data = await self.query_opencellid_api(mcc, mnc, lac, cid)
            
            if tower_data:
                # Cache the result
                await self.cache_tower(mcc, mnc, lac, cid, tower_data)
                logger.info(f"Tower {cid} fetched from OpenCellID and cached")
                return tower_data
            else:
                logger.warning(f"Tower {cid} not found in OpenCellID")
                return None
                
        except Exception as e:
            logger.error(f"Error getting tower location: {e}")
            return None
    
    async def query_opencellid_api(
        self, 
        mcc: int, 
        mnc: int, 
        lac: int, 
        cid: int
    ) -> Optional[Dict[str, Any]]:
        """Query OpenCellID API for tower location"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                params = {
                    "key": self.api_key,
                    "mcc": mcc,
                    "mnc": mnc,
                    "lac": lac,
                    "cellid": cid,
                    "format": "json"
                }
                
                response = await client.get(OPENCELLID_BASE_URL, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check if valid response
                    if "lat" in data and "lon" in data:
                        return {
                            "lat": float(data["lat"]),
                            "lon": float(data["lon"]),
                            "range": int(data.get("range", 1000)),  # Coverage radius in meters
                            "samples": int(data.get("samples", 1)),  # Number of samples
                            "radio": data.get("radio", "GSM"),
                            "created": data.get("created"),
                            "updated": data.get("updated"),
                            "source": "opencellid"
                        }
                    else:
                        logger.warning(f"Invalid response from OpenCellID: {data}")
                        return None
                        
                elif response.status_code == 404:
                    logger.info(f"Tower not found in OpenCellID: {cid}")
                    return None
                else:
                    logger.error(f"OpenCellID API error: {response.status_code}")
                    return None
                    
        except httpx.TimeoutException:
            logger.error("OpenCellID API timeout")
            return None
        except Exception as e:
            logger.error(f"Error querying OpenCellID: {e}")
            return None
    
    async def get_cached_tower(
        self, 
        mcc: int, 
        mnc: int, 
        lac: int, 
        cid: int
    ) -> Optional[Dict[str, Any]]:
        """Get tower from local MongoDB cache"""
        try:
            if not self.cache_collection:
                return None
                
            tower = await self.cache_collection.find_one({
                "mcc": mcc,
                "mnc": mnc,
                "lac": lac,
                "cid": cid
            })
            
            if tower:
                return {
                    "lat": tower["lat"],
                    "lon": tower["lon"],
                    "range": tower.get("range", 1000),
                    "samples": tower.get("samples", 1),
                    "radio": tower.get("radio", "GSM"),
                    "source": tower.get("source", "cache")
                }
            return None
            
        except Exception as e:
            logger.error(f"Error getting cached tower: {e}")
            return None
    
    async def cache_tower(
        self, 
        mcc: int, 
        mnc: int, 
        lac: int, 
        cid: int, 
        tower_data: Dict[str, Any]
    ):
        """Cache tower data in MongoDB"""
        try:
            if not self.cache_collection:
                logger.warning("MongoDB not connected, skipping tower cache")
                return
                
            await self.cache_collection.update_one(
                {
                    "mcc": mcc,
                    "mnc": mnc,
                    "lac": lac,
                    "cid": cid
                },
                {
                    "$set": {
                        **tower_data,
                        "mcc": mcc,
                        "mnc": mnc,
                        "lac": lac,
                        "cid": cid
                    }
                },
                upsert=True
            )
            logger.info(f"Tower {cid} cached successfully")
            
        except Exception as e:
            logger.error(f"Error caching tower: {e}")
    
    async def get_mock_tower_fallback(self, cid: int) -> Optional[Dict[str, Any]]:
        """
        Fallback to mock tower data if OpenCellID fails
        Used for demo/testing with Knowledge Park mock towers
        """
        mock_towers = {
            12345: {"lat": 28.4744, "lon": 77.4860, "range": 800, "name": "Tower KP1-A"},
            12346: {"lat": 28.4686, "lon": 77.4950, "range": 800, "name": "Tower KP2-A"},
            12347: {"lat": 28.4640, "lon": 77.5045, "range": 800, "name": "Tower KP3-A"},
            12348: {"lat": 28.4670, "lon": 77.4980, "range": 800, "name": "Tower Alpha-A"},
        }
        
        if cid in mock_towers:
            logger.info(f"Using mock tower data for {cid}")
            return {
                **mock_towers[cid],
                "source": "mock",
                "samples": 100,
                "radio": "GSM"
            }
        
        return None

# Global instance
opencellid_service = OpenCellIDService()
