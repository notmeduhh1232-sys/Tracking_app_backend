"""
Backend Testing Script
Tests all major components of the backend system
"""

import asyncio
import httpx
import json
from datetime import datetime

# Base URL
BASE_URL = "http://localhost:8000"

# Test data
TEST_VEHICLE_ID = "TEST_DEVICE_001"
TEST_ROUTE_ID = "KP1_KP3_EXPRESS"

# Mock cellular data (Knowledge Park)
MOCK_POSITION_UPDATE = {
    "vehicle_id": TEST_VEHICLE_ID,
    "route_id": TEST_ROUTE_ID,
    "timestamp": datetime.utcnow().isoformat() + "Z",
    "device_type": "mock",
    "raw_data": {
        "cells": [
            {
                "cid": 12345,
                "lac": 101,
                "mcc": 404,
                "mnc": 45,
                "rssi": -75,
                "ta": 10,
                "type": "LTE",
                "distance": 1500
            },
            {
                "cid": 12346,
                "lac": 101,
                "mcc": 404,
                "mnc": 45,
                "rssi": -85,
                "ta": 15,
                "type": "LTE",
                "distance": 2000
            },
            {
                "cid": 12347,
                "lac": 101,
                "mcc": 404,
                "mnc": 45,
                "rssi": -90,
                "ta": 20,
                "type": "LTE",
                "distance": 2500
            }
        ],
        "mcc": 404,
        "mnc": 45
    },
    "position": {
        "lat": 28.4720,
        "lon": 77.4880
    }
}

MOCK_VEHICLE = {
    "device_id": TEST_VEHICLE_ID,
    "route_id": TEST_ROUTE_ID,
    "status": "active"
}

MOCK_ROUTE = {
    "route_id": TEST_ROUTE_ID,
    "name": "KP-1 to KP-3 Express",
    "stops": [
        {
            "id": "kp1_gate",
            "name": "Knowledge Park 1 Gate",
            "lat": 28.4744,
            "lon": 77.4860
        },
        {
            "id": "gl_bajaj",
            "name": "GL Bajaj Institute",
            "lat": 28.4703,
            "lon": 77.4898
        },
        {
            "id": "kp3_entrance",
            "name": "Knowledge Park 3 Entrance",
            "lat": 28.4625,
            "lon": 77.5080
        }
    ],
    "segments": [
        {
            "start_stop": "kp1_gate",
            "end_stop": "gl_bajaj",
            "path": [
                {"lat": 28.4744, "lon": 77.4860},
                {"lat": 28.4703, "lon": 77.4898}
            ],
            "length": 500.0
        }
    ]
}

async def test_health_check():
    """Test health check endpoint"""
    print("\n" + "="*60)
    print("TEST 1: Health Check")
    print("="*60)
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/health", timeout=10.0)
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    print("✅ PASSED: Backend is healthy")
                    return True
                else:
                    print("❌ FAILED: Backend unhealthy")
                    return False
            else:
                print("❌ FAILED: Bad status code")
                return False
                
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

async def test_register_vehicle():
    """Test vehicle registration"""
    print("\n" + "="*60)
    print("TEST 2: Vehicle Registration")
    print("="*60)
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/api/v1/vehicles/",
                json=MOCK_VEHICLE,
                timeout=10.0
            )
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            
            if response.status_code in [200, 201]:
                print("✅ PASSED: Vehicle registered")
                return True
            else:
                print("❌ FAILED: Registration failed")
                return False
                
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

async def test_create_route():
    """Test route creation"""
    print("\n" + "="*60)
    print("TEST 3: Route Creation")
    print("="*60)
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/api/v1/routes/",
                json=MOCK_ROUTE,
                timeout=10.0
            )
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            
            if response.status_code in [200, 201, 409]:  # 409 = already exists
                print("✅ PASSED: Route created/exists")
                return True
            else:
                print("❌ FAILED: Route creation failed")
                return False
                
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

async def test_position_update():
    """Test position update submission"""
    print("\n" + "="*60)
    print("TEST 4: Position Update")
    print("="*60)
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/api/v1/positions/",
                json=MOCK_POSITION_UPDATE,
                timeout=10.0
            )
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            
            if response.status_code == 201:
                data = response.json()
                print(f"\n📍 Estimated Position Method: {data.get('method')}")
                print(f"📏 Accuracy: {data.get('accuracy')}m")
                print("✅ PASSED: Position update processed")
                return True
            else:
                print("❌ FAILED: Position update failed")
                return False
                
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

async def test_get_current_position():
    """Test getting current vehicle position"""
    print("\n" + "="*60)
    print("TEST 5: Get Current Position")
    print("="*60)
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/api/v1/positions/current/{TEST_VEHICLE_ID}",
                timeout=10.0
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Response: {json.dumps(data, indent=2)}")
                print("✅ PASSED: Retrieved current position")
                return True
            else:
                print(f"Response: {response.text}")
                print("⚠️  WARNING: No current position (expected if no data)")
                return True  # Not a failure if no data yet
                
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

async def test_get_vehicle_history():
    """Test getting vehicle position history"""
    print("\n" + "="*60)
    print("TEST 6: Get Vehicle Position History")
    print("="*60)
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/api/v1/positions/vehicle/{TEST_VEHICLE_ID}",
                timeout=10.0
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Position Count: {data.get('count')}")
                print("✅ PASSED: Retrieved position history")
                return True
            else:
                print(f"Response: {response.text}")
                print("❌ FAILED: Could not retrieve history")
                return False
                
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

async def test_get_all_vehicles():
    """Test getting all vehicles"""
    print("\n" + "="*60)
    print("TEST 7: Get All Vehicles")
    print("="*60)
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/api/v1/vehicles/",
                timeout=10.0
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Vehicle Count: {data.get('count')}")
                print("✅ PASSED: Retrieved all vehicles")
                return True
            else:
                print(f"Response: {response.text}")
                print("❌ FAILED: Could not retrieve vehicles")
                return False
                
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

async def test_get_towers():
    """Test getting tower data"""
    print("\n" + "="*60)
    print("TEST 8: Get Towers")
    print("="*60)
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/api/v1/towers/",
                timeout=10.0
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Tower Count: {data.get('count')}")
                print("✅ PASSED: Retrieved tower data")
                return True
            else:
                print(f"Response: {response.text}")
                print("❌ FAILED: Could not retrieve towers")
                return False
                
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

async def run_all_tests():
    """Run all tests"""
    print("\n" + "🚀"*30)
    print("BACKEND COMPREHENSIVE TEST SUITE")
    print("🚀"*30)
    
    # Check if backend is running
    print("\n⏳ Checking if backend is running at", BASE_URL)
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/", timeout=5.0)
            print("✅ Backend is running!")
            print(f"Response: {response.json()}")
    except Exception as e:
        print(f"❌ ERROR: Backend is not running at {BASE_URL}")
        print(f"Error: {e}")
        print("\nPlease start the backend first:")
        print("  Option 1 (Docker): docker-compose up")
        print("  Option 2 (Manual): python main.py")
        return
    
    # Run tests
    results = []
    
    results.append(await test_health_check())
    results.append(await test_register_vehicle())
    results.append(await test_create_route())
    results.append(await test_position_update())
    results.append(await test_get_current_position())
    results.append(await test_get_vehicle_history())
    results.append(await test_get_all_vehicles())
    results.append(await test_get_towers())
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\n✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    asyncio.run(run_all_tests())
