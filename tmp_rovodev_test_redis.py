"""
Quick test to verify Redis connection
"""

import asyncio
import redis.asyncio as redis
from dotenv import load_dotenv
import os

load_dotenv()

async def test_redis_connection():
    print("=" * 60)
    print("REDIS CONNECTION TEST")
    print("=" * 60)
    
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_port = int(os.getenv("REDIS_PORT", "6379"))
    redis_password = os.getenv("REDIS_PASSWORD", "")
    redis_db = int(os.getenv("REDIS_DB", "0"))
    
    print(f"\n📍 Connecting to Redis:")
    print(f"   Host: {redis_host}")
    print(f"   Port: {redis_port}")
    print(f"   Database: {redis_db}")
    print(f"   Password: {'*' * len(redis_password) if redis_password else '(none)'}")
    
    try:
        # Build connection kwargs
        redis_kwargs = {
            "host": redis_host,
            "port": redis_port,
            "db": redis_db,
            "decode_responses": True
        }
        
        if redis_password:
            redis_kwargs["password"] = redis_password
        
        # Connect
        client = redis.Redis(**redis_kwargs)
        
        # Test PING
        print("\n⏳ Testing connection...")
        response = await client.ping()
        print(f"✅ PING: {response}")
        
        # Test SET
        print("\n⏳ Testing SET operation...")
        await client.set("test_key", "Hello from GPS-Free Tracking!")
        print("✅ SET: test_key = 'Hello from GPS-Free Tracking!'")
        
        # Test GET
        print("\n⏳ Testing GET operation...")
        value = await client.get("test_key")
        print(f"✅ GET: test_key = '{value}'")
        
        # Test DELETE
        print("\n⏳ Testing DELETE operation...")
        await client.delete("test_key")
        print("✅ DELETE: test_key removed")
        
        # Get Redis info
        print("\n⏳ Getting Redis info...")
        info = await client.info("server")
        print(f"✅ Redis Version: {info.get('redis_version', 'Unknown')}")
        print(f"✅ OS: {info.get('os', 'Unknown')}")
        
        # Close connection
        await client.close()
        
        print("\n" + "=" * 60)
        print("🎉 ALL REDIS TESTS PASSED!")
        print("=" * 60)
        print("\n✅ Redis is connected and working correctly")
        print("✅ Backend can use Redis for caching")
        
        return True
        
    except Exception as e:
        print("\n" + "=" * 60)
        print("❌ REDIS CONNECTION FAILED")
        print("=" * 60)
        print(f"\nError: {e}")
        print("\nPlease check:")
        print("  1. Redis host and port are correct")
        print("  2. Redis password is correct")
        print("  3. Firewall allows connection")
        print("  4. Redis Cloud database is active")
        
        return False

if __name__ == "__main__":
    asyncio.run(test_redis_connection())
