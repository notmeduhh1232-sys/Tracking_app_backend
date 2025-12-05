from fastapi import APIRouter, HTTPException, status
from datetime import datetime
from app.models.schemas import Vehicle
from app.database import mongodb
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/")
async def get_all_vehicles():
    """Get all vehicles"""
    
    try:
        # Check if MongoDB is connected
        if not mongodb.db:
            logger.warning("MongoDB not connected, returning empty vehicles")
            return {"count": 0, "vehicles": []}
        
        cursor = mongodb.db.vehicles.find()
        vehicles = await cursor.to_list(length=1000)
        
        for vehicle in vehicles:
            vehicle["_id"] = str(vehicle["_id"])
            if vehicle.get("last_update"):
                vehicle["last_update"] = vehicle["last_update"].isoformat()
        
        return {"count": len(vehicles), "vehicles": vehicles}
        
    except Exception as e:
        logger.error(f"Error fetching vehicles: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/{device_id}")
async def get_vehicle(device_id: str):
    """Get specific vehicle"""
    
    try:
        vehicle = await mongodb.db.vehicles.find_one({"device_id": device_id})
        
        if not vehicle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehicle not found"
            )
        
        vehicle["_id"] = str(vehicle["_id"])
        if vehicle.get("last_update"):
            vehicle["last_update"] = vehicle["last_update"].isoformat()
        
        return vehicle
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching vehicle: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/", status_code=status.HTTP_201_CREATED)
async def register_vehicle(vehicle: Vehicle):
    """Register a new vehicle"""
    
    try:
        # Check if already exists
        existing = await mongodb.db.vehicles.find_one({"device_id": vehicle.device_id})
        if existing:
            # Update instead
            await mongodb.db.vehicles.update_one(
                {"device_id": vehicle.device_id},
                {"$set": vehicle.dict()}
            )
            return {"device_id": vehicle.device_id, "status": "updated"}
        
        vehicle_doc = vehicle.dict()
        vehicle_doc["created_at"] = datetime.utcnow()
        
        result = await mongodb.db.vehicles.insert_one(vehicle_doc)
        
        return {
            "id": str(result.inserted_id),
            "device_id": vehicle.device_id,
            "status": "created"
        }
        
    except Exception as e:
        logger.error(f"Error registering vehicle: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
