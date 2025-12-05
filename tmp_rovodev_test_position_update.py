"""
Test position update endpoint specifically to see the error
"""

import asyncio
import httpx
import json
from datetime import datetime, timezone

BASE_URL = "http://localhost:8000"

MOCK_POSITION_UPDATE = {
    "vehicle_id": "TEST_DEVICE_001",
    "route_id": "KP1_KP3_EXPRESS",
    "timestamp": datetime.now(timezone.utc).isoformat(),
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

async def test_position_update():
    print("=" * 60)
    print("TESTING POSITION UPDATE")
    print("=" * 60)
    
    print("\nSending position update...")
    print(f"Vehicle: {MOCK_POSITION_UPDATE['vehicle_id']}")
    print(f"Route: {MOCK_POSITION_UPDATE['route_id']}")
    print(f"Cells: {len(MOCK_POSITION_UPDATE['raw_data']['cells'])}")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/api/v1/positions/",
                json=MOCK_POSITION_UPDATE,
                timeout=30.0
            )
            
            print(f"\nStatus Code: {response.status_code}")
            
            if response.status_code in [200, 201]:
                data = response.json()
                print(f"Response: {json.dumps(data, indent=2)}")
                print("\n✅ SUCCESS: Position update processed")
            else:
                print(f"Response: {response.text}")
                print("\n❌ FAILED: Position update failed")
                
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_position_update())
