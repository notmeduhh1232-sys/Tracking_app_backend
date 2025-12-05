"""
Quick test to verify MongoDB connection
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv()

async def test_mongodb_connection():
    print("=" * 60)
    print("MONGODB CONNECTION TEST")
    print("=" * 60)
    
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    mongodb_db = os.getenv("MONGODB_DB_NAME", "vehicle_tracking")
    
    print(f"\n📍 Connecting to MongoDB:")
    print(f"   URL: {mongodb_url}")
    print(f"   Database: {mongodb_db}")
    
    try:
        # Connect
        print("\n⏳ Testing connection...")
        client = AsyncIOMotorClient(mongodb_url)
        
        # Test connection with ping
        await client.admin.command('ping')
        print("✅ PING: Success")
        
        # Get database
        db = client[mongodb_db]
        
        # Test write operation
        print("\n⏳ Testing WRITE operation...")
        test_collection = db.test_connection
        result = await test_collection.insert_one({
            "test": "Hello from GPS-Free Tracking!",
            "timestamp": "2024-01-15T10:00:00Z"
        })
        print(f"✅ INSERT: Document ID = {result.inserted_id}")
        
        # Test read operation
        print("\n⏳ Testing READ operation...")
        doc = await test_collection.find_one({"_id": result.inserted_id})
        print(f"✅ FIND: {doc.get('test')}")
        
        # Test delete operation
        print("\n⏳ Testing DELETE operation...")
        await test_collection.delete_one({"_id": result.inserted_id})
        print("✅ DELETE: Test document removed")
        
        # Get server info
        print("\n⏳ Getting MongoDB info...")
        server_info = await client.server_info()
        print(f"✅ MongoDB Version: {server_info.get('version', 'Unknown')}")
        
        # List collections
        collections = await db.list_collection_names()
        print(f"✅ Collections: {len(collections)} found")
        if collections:
            print(f"   {', '.join(collections[:5])}")
        
        # Close connection
        client.close()
        
        print("\n" + "=" * 60)
        print("🎉 ALL MONGODB TESTS PASSED!")
        print("=" * 60)
        print("\n✅ MongoDB is connected and working correctly")
        print("✅ Backend can use MongoDB for storage")
        
        return True
        
    except Exception as e:
        print("\n" + "=" * 60)
        print("❌ MONGODB CONNECTION FAILED")
        print("=" * 60)
        print(f"\nError: {e}")
        print("\n📋 Options to fix:")
        print("\n  Option 1: Use MongoDB Atlas (Cloud - Free)")
        print("    1. Go to https://www.mongodb.com/cloud/atlas/register")
        print("    2. Create free M0 cluster (takes 5 minutes)")
        print("    3. Click 'Connect' → 'Connect your application'")
        print("    4. Copy connection string")
        print("    5. Update backend/.env:")
        print("       MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/vehicle_tracking")
        print("\n  Option 2: Install MongoDB Locally")
        print("    1. Download: https://www.mongodb.com/try/download/community")
        print("    2. Install with default settings")
        print("    3. MongoDB will run on localhost:27017")
        print("\n  Option 3: Use Docker")
        print("    docker run -d -p 27017:27017 --name mongo mongo:7.0")
        
        return False

if __name__ == "__main__":
    asyncio.run(test_mongodb_connection())
