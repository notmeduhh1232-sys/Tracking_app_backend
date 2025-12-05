# 🧪 Backend Testing Guide

Complete guide for testing the GPS-Free Vehicle Tracking Backend.

---

## 📋 Prerequisites

Before testing, ensure you have:

1. **Python 3.11+** installed
2. **MongoDB** running (localhost:27017 or MongoDB Atlas)
3. **Redis** running (localhost:6379 - optional but recommended)
4. **Backend dependencies** installed

---

## 🚀 Quick Start Testing

### Option 1: Using Docker (Easiest)

```bash
# Start everything (MongoDB + Redis + Backend)
cd backend
docker-compose up

# Wait for services to start (30 seconds)
# Backend will be at: http://localhost:8000
```

### Option 2: Manual Setup

```bash
# Terminal 1: Start MongoDB (if using Docker)
docker run -d -p 27017:27017 --name mongo mongo:7.0

# Terminal 2: Start Redis (if using Docker)
docker run -d -p 6379:6379 --name redis redis:7.2-alpine

# Terminal 3: Start Backend
cd backend
pip install -r requirements.txt
python main.py
```

---

## 🧪 Running Tests

### Automated Test Suite

We've created a comprehensive test script:

```bash
cd backend
python tmp_rovodev_test_backend.py
```

This will test:
- ✅ Health check
- ✅ Vehicle registration
- ✅ Route creation
- ✅ Position updates
- ✅ Position retrieval
- ✅ Position history
- ✅ Vehicle listing
- ✅ Tower data

### Expected Output

```
🚀🚀🚀 BACKEND COMPREHENSIVE TEST SUITE 🚀🚀🚀

⏳ Checking if backend is running...
✅ Backend is running!

============================================================
TEST 1: Health Check
============================================================
Status Code: 200
Response: {
  "status": "healthy",
  "mongodb": true,
  "redis": true
}
✅ PASSED: Backend is healthy

... (more tests)

============================================================
TEST SUMMARY
============================================================

✅ Passed: 8/8
❌ Failed: 0/8

🎉 ALL TESTS PASSED!
```

---

## 🔧 Manual Testing with cURL

### 1. Health Check

```bash
curl http://localhost:8000/health
```

Expected:
```json
{
  "status": "healthy",
  "mongodb": true,
  "redis": true
}
```

### 2. Register a Vehicle

```bash
curl -X POST http://localhost:8000/api/v1/vehicles/ \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "TEST_DEVICE_001",
    "route_id": "KP1_KP3_EXPRESS",
    "status": "active"
  }'
```

### 3. Create a Route

```bash
curl -X POST http://localhost:8000/api/v1/routes/ \
  -H "Content-Type: application/json" \
  -d '{
    "route_id": "KP1_KP3_EXPRESS",
    "name": "KP-1 to KP-3 Express",
    "stops": [
      {"id": "kp1", "name": "Knowledge Park 1", "lat": 28.4744, "lon": 77.4860},
      {"id": "kp3", "name": "Knowledge Park 3", "lat": 28.4625, "lon": 77.5080}
    ],
    "segments": []
  }'
```

### 4. Submit Position Update

```bash
curl -X POST http://localhost:8000/api/v1/positions/ \
  -H "Content-Type: application/json" \
  -d '{
    "vehicle_id": "TEST_DEVICE_001",
    "route_id": "KP1_KP3_EXPRESS",
    "timestamp": "2024-01-15T10:30:00Z",
    "device_type": "mock",
    "raw_data": {
      "cells": [
        {
          "cid": 12345,
          "lac": 101,
          "mcc": 404,
          "mnc": 45,
          "rssi": -75,
          "ta": 10
        }
      ],
      "mcc": 404,
      "mnc": 45
    },
    "position": {
      "lat": 28.4720,
      "lon": 77.4880
    }
  }'
```

### 5. Get Current Position

```bash
curl http://localhost:8000/api/v1/positions/current/TEST_DEVICE_001
```

### 6. Get Position History

```bash
curl http://localhost:8000/api/v1/positions/vehicle/TEST_DEVICE_001
```

### 7. List All Vehicles

```bash
curl http://localhost:8000/api/v1/vehicles/
```

### 8. Get Towers

```bash
curl http://localhost:8000/api/v1/towers/
```

---

## 🌐 Testing with API Documentation

FastAPI provides interactive API documentation:

1. **Swagger UI**: http://localhost:8000/docs
2. **ReDoc**: http://localhost:8000/redoc

You can test all endpoints directly from your browser!

---

## 🔍 Testing Position Estimation

The backend implements 3 positioning methods:

### Method 1: Triangulation with Timing Advance (Best)
- **Accuracy**: ~175m
- **Requires**: 3+ cell towers with TA data
- **Test**: Send position update with 3+ cells having `ta` values

```json
{
  "cells": [
    {"cid": 12345, "lac": 101, "mcc": 404, "mnc": 45, "rssi": -75, "ta": 10},
    {"cid": 12346, "lac": 101, "mcc": 404, "mnc": 45, "rssi": -85, "ta": 15},
    {"cid": 12347, "lac": 101, "mcc": 404, "mnc": 45, "rssi": -90, "ta": 20}
  ]
}
```

### Method 2: Weighted Centroid (Good)
- **Accuracy**: ~400m
- **Requires**: 2+ cell towers with RSSI
- **Test**: Send position update with 2+ cells (no TA)

### Method 3: Cell-ID Fallback (Basic)
- **Accuracy**: ~800m
- **Requires**: 1 cell tower
- **Test**: Send position update with 1 cell

---

## 🧩 Integration Testing

### Test with Driver App

1. Start backend: `docker-compose up`
2. Start driver app (see APPLICATION1-driver-app/)
3. In driver app:
   - Enable Demo Mode
   - Select route
   - Start tracking
4. Monitor backend logs for incoming position updates

### Expected Flow

```
Backend <- POST /api/v1/positions/ <- Driver App
Backend -> Process cellular data
Backend -> Estimate position
Backend -> Save to MongoDB
Backend -> Cache in Redis
Backend -> Broadcast via WebSocket
```

---

## 📊 Monitoring & Debugging

### Check Backend Logs

```bash
docker-compose logs -f backend
```

### Check MongoDB Data

```bash
# Connect to MongoDB
docker exec -it vehicle_tracking_mongodb mongosh

# Switch to database
use vehicle_tracking

# Check collections
show collections

# View positions
db.positions.find().pretty()

# View vehicles
db.vehicles.find().pretty()

# View towers
db.towers.find().pretty()
```

### Check Redis Cache

```bash
# Connect to Redis
docker exec -it vehicle_tracking_redis redis-cli

# List all keys
KEYS *

# Get vehicle position
GET vehicle:position:TEST_DEVICE_001

# Check cache stats
INFO stats
```

---

## 🐛 Common Issues

### Issue 1: "MongoDB connection failed"

**Solution:**
- Ensure MongoDB is running: `docker ps | grep mongo`
- Check connection string in `.env`: `MONGODB_URL=mongodb://localhost:27017`
- If using Docker: `docker-compose up mongodb`

### Issue 2: "Redis connection failed"

**Solution:**
- Ensure Redis is running: `docker ps | grep redis`
- Redis is optional - backend will work without it (but slower)
- If using Docker: `docker-compose up redis`

### Issue 3: "No tower data found"

**Solution:**
- Mock towers are pre-configured for Knowledge Park
- For real cellular data, you need OpenCellID API key
- Set in `.env`: `OPENCELLID_API_KEY=your_key_here`

### Issue 4: "Module not found"

**Solution:**
```bash
cd backend
pip install -r requirements.txt
```

### Issue 5: "Port 8000 already in use"

**Solution:**
```bash
# Find process using port 8000
netstat -ano | findstr :8000  # Windows
lsof -i :8000                  # Mac/Linux

# Kill the process or change port in .env
PORT=8001
```

---

## ✅ Test Checklist

Before deploying, verify:

- [ ] Health check returns "healthy"
- [ ] MongoDB connection works
- [ ] Redis connection works (optional)
- [ ] Can register vehicles
- [ ] Can create routes
- [ ] Can submit position updates
- [ ] Position estimation works (all 3 methods)
- [ ] Can retrieve current position
- [ ] Can retrieve position history
- [ ] WebSocket connections work
- [ ] API documentation accessible at /docs

---

## 🎯 Performance Testing

### Load Test Position Updates

```bash
# Install Apache Bench (if needed)
# Windows: Download from https://www.apachelounge.com/download/

# Send 100 requests
ab -n 100 -c 10 -p position_data.json -T application/json \
  http://localhost:8000/api/v1/positions/
```

### Expected Performance

- Health check: < 50ms
- Position update: < 200ms
- Position retrieval: < 100ms
- WebSocket broadcast: < 50ms

---

## 📝 Next Steps

After backend testing is complete:

1. ✅ Verify all endpoints work
2. ✅ Test integration with driver app
3. 🚧 Build commuter app (APPLICATION 2)
4. 🚧 Test end-to-end system
5. 🚧 Deploy to production

---

## 🆘 Need Help?

If tests fail, check:
1. Backend logs: `docker-compose logs backend`
2. MongoDB logs: `docker-compose logs mongodb`
3. Network connectivity: `curl http://localhost:8000/health`
4. Port availability: `netstat -ano | findstr :8000`

Happy Testing! 🚀
