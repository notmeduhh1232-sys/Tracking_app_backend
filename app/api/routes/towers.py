from fastapi import APIRouter, HTTPException, status
from app.models.schemas import Tower
from app.database import mongodb
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/")
async def get_all_towers(limit: int = 100):
    """Get all cached towers"""
    
    try:
        cursor = mongodb.db.towers.find().limit(limit)
        towers = await cursor.to_list(length=limit)
        
        for tower in towers:
            tower["_id"] = str(tower["_id"])
        
        return {"count": len(towers), "towers": towers}
        
    except Exception as e:
        logger.error(f"Error fetching towers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/nearby")
async def get_nearby_towers(lat: float, lon: float, radius_meters: int = 5000):
    """Get towers near a location"""
    
    try:
        # GeoJSON query
        towers = await mongodb.db.towers.find({
            "location": {
                "$near": {
                    "$geometry": {
                        "type": "Point",
                        "coordinates": [lon, lat]
                    },
                    "$maxDistance": radius_meters
                }
            }
        }).to_list(length=50)
        
        for tower in towers:
            tower["_id"] = str(tower["_id"])
        
        return {"count": len(towers), "towers": towers}
        
    except Exception as e:
        logger.error(f"Error fetching nearby towers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
