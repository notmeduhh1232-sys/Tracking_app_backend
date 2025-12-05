from fastapi import APIRouter, HTTPException, status
from typing import List
from datetime import datetime
from bson import ObjectId

from app.models.schemas import PositionUpdate, PositionResponse
from app.database import mongodb, redis_client
from app.services.positioning import positioning_engine
from app.services.websocket_manager import manager
import logging
import json

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_position_update(update: PositionUpdate):
    """
    Receive position update from driver app and estimate position
    """
    
    try:
        logger.info(f"Received position update from vehicle: {update.vehicle_id}")
        
        # Estimate position using positioning engine (now with OpenCellID integration)
        estimated_position = None
        accuracy = 0
        method = "none"
        
        # Try to estimate position from cellular data
        position, accuracy, method = await positioning_engine.estimate_position(
            update.raw_data.cells
        )
        
        if position:
            estimated_position = {
                "type": "Point",
                "coordinates": [position.lon, position.lat]  # GeoJSON: [lon, lat]
            }
        elif update.position:
            # Fallback to provided position (demo mode)
            estimated_position = {
                "type": "Point",
                "coordinates": [update.position.lon, update.position.lat]
            }
            accuracy = 50  # Demo mode has perfect accuracy
            method = "demo_mode"
        
        # Save to MongoDB
        position_doc = {
            "vehicle_id": update.vehicle_id,
            "route_id": update.route_id,
            "timestamp": datetime.fromisoformat(update.timestamp.replace('Z', '+00:00')),
            "raw_data": {
                "cells": [cell.dict() for cell in update.raw_data.cells],
                "mcc": update.raw_data.mcc,
                "mnc": update.raw_data.mnc
            },
            "estimated_position": estimated_position,
            "accuracy": accuracy,
            "method": method,
            "device_type": update.device_type,
            "created_at": datetime.utcnow()
        }
        
        result = await mongodb.db.positions.insert_one(position_doc)
        
        # Cache current position in Redis
        if redis_client.client and estimated_position:
            cache_key = f"vehicle:position:{update.vehicle_id}"
            cache_data = {
                "vehicle_id": update.vehicle_id,
                "position": estimated_position,
                "accuracy": accuracy,
                "method": method,
                "timestamp": update.timestamp
            }
            
            try:
                await redis_client.client.setex(
                    cache_key,
                    300,  # 5 minutes
                    json.dumps(cache_data)
                )
            except Exception as e:
                logger.warning(f"Redis cache error: {e}")
        
        # Broadcast update to WebSocket clients
        broadcast_data = {
            "type": "position_update",
            "vehicle_id": update.vehicle_id,
            "route_id": update.route_id,
            "position": estimated_position,
            "accuracy": accuracy,
            "method": method,
            "timestamp": update.timestamp
        }
        await manager.broadcast(broadcast_data)
        
        logger.info(f"Position saved: {method}, accuracy: {accuracy}m")
        
        return {
            "id": str(result.inserted_id),
            "vehicle_id": update.vehicle_id,
            "estimated_position": estimated_position,
            "accuracy": accuracy,
            "method": method,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error processing position update: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing position: {str(e)}"
        )

@router.get("/vehicle/{vehicle_id}")
async def get_vehicle_positions(
    vehicle_id: str,
    limit: int = 100
):
    """Get recent positions for a vehicle"""
    
    try:
        cursor = mongodb.db.positions.find(
            {"vehicle_id": vehicle_id}
        ).sort("timestamp", -1).limit(limit)
        
        positions = await cursor.to_list(length=limit)
        
        # Convert ObjectId to string
        for pos in positions:
            pos["_id"] = str(pos["_id"])
            pos["timestamp"] = pos["timestamp"].isoformat()
        
        return {
            "vehicle_id": vehicle_id,
            "count": len(positions),
            "positions": positions
        }
        
    except Exception as e:
        logger.error(f"Error fetching positions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/current/{vehicle_id}")
async def get_current_position(vehicle_id: str):
    """Get current position of a vehicle (from Redis cache or MongoDB)"""
    
    try:
        # Try Redis first
        if redis_client.client:
            cache_key = f"vehicle:position:{vehicle_id}"
            try:
                cached = await redis_client.client.get(cache_key)
                if cached:
                    return json.loads(cached)
            except Exception as e:
                logger.warning(f"Redis error: {e}")
        
        # Fallback to MongoDB
        position = await mongodb.db.positions.find_one(
            {"vehicle_id": vehicle_id},
            sort=[("timestamp", -1)]
        )
        
        if not position:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No position found for vehicle"
            )
        
        position["_id"] = str(position["_id"])
        position["timestamp"] = position["timestamp"].isoformat()
        
        return position
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching current position: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
