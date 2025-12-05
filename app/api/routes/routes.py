from fastapi import APIRouter, HTTPException, status
from typing import List
from app.models.schemas import Route, RouteSegment, Stop, Position
from app.database import mongodb
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/")
async def get_all_routes():
    """Get all routes"""
    
    try:
        cursor = mongodb.db.routes.find()
        routes = await cursor.to_list(length=100)
        
        for route in routes:
            route["_id"] = str(route["_id"])
        
        return {"count": len(routes), "routes": routes}
        
    except Exception as e:
        logger.error(f"Error fetching routes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/{route_id}")
async def get_route(route_id: str):
    """Get specific route details"""
    
    try:
        route = await mongodb.db.routes.find_one({"route_id": route_id})
        
        if not route:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Route not found"
            )
        
        route["_id"] = str(route["_id"])
        return route
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching route: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_route(route: Route):
    """Create a new route"""
    
    try:
        # Check if route already exists
        existing = await mongodb.db.routes.find_one({"route_id": route.route_id})
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Route already exists"
            )
        
        route_doc = route.dict()
        result = await mongodb.db.routes.insert_one(route_doc)
        
        return {
            "id": str(result.inserted_id),
            "route_id": route.route_id,
            "status": "created"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating route: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
