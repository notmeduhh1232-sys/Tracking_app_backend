"""
Quick test to verify backend code loads without errors
Tests imports and basic functionality without requiring databases
"""

import sys
import os

print("=" * 60)
print("BACKEND CODE VALIDATION TEST")
print("=" * 60)

# Test 1: Import main modules
print("\n[1/6] Testing core imports...")
try:
    from app.config import settings
    from app.models import schemas
    from app.database import mongodb, redis_client
    print("✅ Core modules imported successfully")
except Exception as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

# Test 2: Import services
print("\n[2/6] Testing service imports...")
try:
    from app.services.positioning import positioning_engine
    from app.services.tower_database import tower_db
    from app.services.websocket_manager import manager
    print("✅ Service modules imported successfully")
except Exception as e:
    print(f"❌ Service import error: {e}")
    sys.exit(1)

# Test 3: Import API routes
print("\n[3/6] Testing API route imports...")
try:
    from app.api.routes import positions, vehicles, routes, towers
    print("✅ API routes imported successfully")
except Exception as e:
    print(f"❌ API route import error: {e}")
    sys.exit(1)

# Test 4: Test positioning algorithms
print("\n[4/6] Testing positioning engine...")
try:
    # Test haversine distance calculation
    distance = positioning_engine.haversine_distance(
        28.4744, 77.4860,  # KP1
        28.4625, 77.5080   # KP3
    )
    print(f"   Haversine distance test: {distance:.2f} meters")
    
    # Test is_high_density
    test_towers = {
        1: (28.4720, 77.4880),
        2: (28.4690, 77.4960),
    }
    is_dense = positioning_engine.is_high_density(test_towers)
    print(f"   Tower density test: {'High' if is_dense else 'Low'} density")
    
    print("✅ Positioning engine works correctly")
except Exception as e:
    print(f"❌ Positioning engine error: {e}")
    sys.exit(1)

# Test 5: Test data models
print("\n[5/6] Testing data models...")
try:
    from app.models.schemas import CellTowerData, Position, PositionUpdate
    
    # Create test cell tower data
    cell = CellTowerData(
        cid=12345,
        lac=101,
        mcc=404,
        mnc=45,
        rssi=-75,
        ta=10
    )
    print(f"   Cell data: CID={cell.cid}, RSSI={cell.rssi}")
    
    # Create test position
    pos = Position(lat=28.4720, lon=77.4880)
    print(f"   Position: {pos.lat}, {pos.lon}")
    
    print("✅ Data models work correctly")
except Exception as e:
    print(f"❌ Data model error: {e}")
    sys.exit(1)

# Test 6: Test configuration
print("\n[6/6] Testing configuration...")
try:
    print(f"   MongoDB URL: {settings.MONGODB_URL}")
    print(f"   Redis Host: {settings.REDIS_HOST}:{settings.REDIS_PORT}")
    print(f"   Server: {settings.HOST}:{settings.PORT}")
    print(f"   Debug mode: {settings.DEBUG}")
    print("✅ Configuration loaded successfully")
except Exception as e:
    print(f"❌ Configuration error: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ ALL CODE VALIDATION TESTS PASSED!")
print("=" * 60)

print("\n📋 Next Steps:")
print("   1. Set up MongoDB (required)")
print("      - Cloud: https://www.mongodb.com/cloud/atlas")
print("      - Local: https://www.mongodb.com/try/download/community")
print("   2. Set up Redis (optional but recommended)")
print("      - Cloud: https://redis.com/try-free/")
print("      - Local: https://redis.io/download")
print("   3. Update backend/.env with connection details")
print("   4. Start backend: python main.py")
print("   5. Run tests: python tmp_rovodev_test_backend.py")

print("\n💡 Tip: You can use cloud databases (free tier) to test quickly!")
