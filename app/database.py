from motor.motor_asyncio import AsyncIOMotorClient
import redis.asyncio as redis
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None
    
    async def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = AsyncIOMotorClient(settings.MONGODB_URL)
            self.db = self.client[settings.MONGODB_DB_NAME]
            
            # Test connection
            await self.client.admin.command('ping')
            logger.info("Connected to MongoDB successfully")
            
            # Create indexes
            await self.create_indexes()
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")
    
    async def is_connected(self):
        """Check if connected to MongoDB"""
        try:
            if self.client:
                await self.client.admin.command('ping')
                return True
        except:
            pass
        return False
    
    async def create_indexes(self):
        """Create database indexes"""
        try:
            # Positions collection - 2dsphere index for geospatial queries
            await self.db.positions.create_index([("estimated_position", "2dsphere")])
            await self.db.positions.create_index([("vehicle_id", 1), ("timestamp", -1)])
            
            # Vehicles collection
            await self.db.vehicles.create_index("device_id", unique=True)
            
            # Routes collection
            await self.db.routes.create_index("route_id", unique=True)
            
            # Towers collection
            await self.db.towers.create_index([("location", "2dsphere")])
            await self.db.towers.create_index([("cid", 1), ("lac", 1), ("mcc", 1), ("mnc", 1)])
            
            logger.info("Database indexes created")
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")

class RedisClient:
    client: redis.Redis = None
    
    async def connect(self):
        """Connect to Redis"""
        try:
            redis_kwargs = {
                "host": settings.REDIS_HOST,
                "port": settings.REDIS_PORT,
                "db": settings.REDIS_DB,
                "decode_responses": True
            }
            
            # Add password if provided
            if settings.REDIS_PASSWORD:
                redis_kwargs["password"] = settings.REDIS_PASSWORD
            
            self.client = redis.Redis(**redis_kwargs)
            
            # Test connection
            await self.client.ping()
            logger.info(f"Connected to Redis successfully at {settings.REDIS_HOST}:{settings.REDIS_PORT}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            # Don't raise - Redis is optional
    
    async def disconnect(self):
        """Disconnect from Redis"""
        if self.client:
            await self.client.close()
            logger.info("Disconnected from Redis")
    
    async def is_connected(self):
        """Check if connected to Redis"""
        try:
            if self.client:
                await self.client.ping()
                return True
        except:
            pass
        return False

# Global instances
mongodb = MongoDB()
redis_client = RedisClient()
