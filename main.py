from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
from typing import List
import logging

from app.database import mongodb, redis_client
from app.api.routes import positions, routes, vehicles, towers
from app.services.websocket_manager import manager
from app.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    logger.info("Starting up backend...")
    await mongodb.connect()
    await redis_client.connect()
    logger.info("Backend started successfully!")
    
    yield
    
    # Shutdown
    logger.info("Shutting down backend...")
    await mongodb.disconnect()
    await redis_client.disconnect()
    logger.info("Backend shutdown complete")

# Create FastAPI app
app = FastAPI(
    title="GPS-Free Vehicle Tracking Backend",
    description="Real-time vehicle tracking using cellular network metadata",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(positions.router, prefix="/api/v1/positions", tags=["positions"])
app.include_router(routes.router, prefix="/api/v1/routes", tags=["routes"])
app.include_router(vehicles.router, prefix="/api/v1/vehicles", tags=["vehicles"])
app.include_router(towers.router, prefix="/api/v1/towers", tags=["towers"])

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and listen for client messages
            data = await websocket.receive_text()
            logger.info(f"Received from client: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("Client disconnected")

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "mongodb": await mongodb.is_connected(),
        "redis": await redis_client.is_connected(),
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "GPS-Free Vehicle Tracking Backend",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
