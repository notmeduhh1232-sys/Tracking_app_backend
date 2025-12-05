# 🚀 Backend Installation & Testing Guide (No Docker)

Since Docker is not available, here's how to set up the backend manually.

---

## 📦 Step 1: Install Python Dependencies

```powershell
cd backend
pip install -r requirements.txt
```

**Verify installation:**
```powershell
python tmp_rovodev_check_dependencies.py
```

---

## 🗄️ Step 2: Set Up Databases

You have **3 options** for databases:

### Option A: Cloud Services (EASIEST - No Installation)

#### MongoDB Atlas (Free Cloud MongoDB)
1. Go to https://www.mongodb.com/cloud/atlas/register
2. Create free account
3. Create a free cluster (M0)
4. Get connection string
5. Update `backend/.env`:
   ```
   MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/vehicle_tracking
   ```

#### Redis Cloud (Free Cloud Redis)
1. Go to https://redis.com/try-free/
2. Create free account
3. Create free database
4. Get connection details
5. Update `backend/.env`:
   ```
   REDIS_HOST=your-redis-host.cloud.redislabs.com
   REDIS_PORT=your-port
   ```

### Option B: Local Installation

#### Install MongoDB Community Edition
1. Download: https://www.mongodb.com/try/download/community
2. Install with default settings
3. MongoDB will run on `localhost:27017`

#### Install Redis (Windows)
1. Download: https://github.com/tporadowski/redis/releases
2. Extract and run `redis-server.exe`
3. Redis will run on `localhost:6379`

### Option C: Use WSL2 with Docker
If you have WSL2, you can run Docker inside WSL2.

---

## 🔧 Step 3: Configure Environment

Edit `backend/.env` file:

```env
# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017
# Or use MongoDB Atlas:
# MONGODB_URL=mongodb+srv://user:pass@cluster.mongodb.net/vehicle_tracking

MONGODB_DB_NAME=vehicle_tracking

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
# Or use Redis Cloud:
# REDIS_HOST=your-redis.cloud.redislabs.com
# REDIS_PORT=12345

# OpenCellID (Optional - for real tower data)
OPENCELLID_API_KEY=

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=True

# CORS Configuration
CORS_ORIGINS=["*"]
```

---

## ▶️ Step 4: Start the Backend

```powershell
cd backend
python main.py
```

**Expected output:**
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Starting up backend...
INFO:     Connected to MongoDB successfully
INFO:     Connected to Redis successfully
INFO:     Backend started successfully!
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

## 🧪 Step 5: Run Tests

**Open a NEW terminal** (keep backend running), then:

```powershell
cd backend
python tmp_rovodev_test_backend.py
```

**Expected output:**
```
🚀🚀🚀 BACKEND COMPREHENSIVE TEST SUITE 🚀🚀🚀

⏳ Checking if backend is running at http://localhost:8000
✅ Backend is running!

============================================================
TEST 1: Health Check
============================================================
✅ PASSED: Backend is healthy

... (8 tests total)

🎉 ALL TESTS PASSED!
```

---

## 🌐 Step 6: Test with Browser

Open your browser and visit:

1. **API Documentation**: http://localhost:8000/docs
   - Interactive API testing interface
   - Try all endpoints directly from browser

2. **Health Check**: http://localhost:8000/health
   - Should show: `{"status": "healthy", "mongodb": true, "redis": true}`

3. **Root**: http://localhost:8000/
   - Shows backend info

---

## 🔍 Testing Position Estimation

The backend has 3 positioning algorithms. Let's test them:

### Test 1: Demo Mode (No Real Towers)

```powershell
# This uses the mock tower data built into the backend
curl -X POST http://localhost:8000/api/v1/positions/ -H "Content-Type: application/json" -d "{\"vehicle_id\":\"TEST_001\",\"route_id\":\"KP1_KP3\",\"timestamp\":\"2024-01-15T10:00:00Z\",\"device_type\":\"mock\",\"raw_data\":{\"cells\":[{\"cid\":12345,\"lac\":101,\"mcc\":404,\"mnc\":45,\"rssi\":-75,\"ta\":10}],\"mcc\":404,\"mnc\":45},\"position\":{\"lat\":28.4720,\"lon\":77.4880}}"
```

Expected response:
```json
{
  "method": "demo_mode",
  "accuracy": 50,
  "status": "success"
}
```

---

## 📊 Monitor Backend

### View Logs
- Backend logs appear in the terminal where you ran `python main.py`
- Look for:
  - `INFO: Received position update from vehicle: XXX`
  - `INFO: Position saved: triangulation_ta, accuracy: 175m`

### Check Database

**MongoDB:**
```powershell
# If MongoDB is local, you can use MongoDB Compass (GUI)
# Download: https://www.mongodb.com/try/download/compass

# Or use mongosh command line:
mongosh
use vehicle_tracking
db.positions.find().pretty()
```

**Redis:**
```powershell
# If Redis is local:
redis-cli
KEYS *
GET vehicle:position:TEST_001
```

---

## ✅ Verification Checklist

Before considering backend "complete", verify:

- [ ] Backend starts without errors
- [ ] Health check shows MongoDB connected
- [ ] Health check shows Redis connected (or warns if unavailable)
- [ ] Can register vehicles via API
- [ ] Can create routes via API
- [ ] Can submit position updates
- [ ] Position estimation works (returns method + accuracy)
- [ ] Can retrieve current position
- [ ] Can retrieve position history
- [ ] API documentation accessible at /docs
- [ ] All 8 tests pass in test suite

---

## 🐛 Troubleshooting

### Error: "ModuleNotFoundError"
```powershell
cd backend
pip install -r requirements.txt
```

### Error: "MongoDB connection failed"
- **Check if MongoDB is running:**
  - Windows: Check Services for "MongoDB"
  - Or run: `mongosh` (should connect)
- **Use cloud MongoDB:**
  - Sign up at https://www.mongodb.com/cloud/atlas
  - Update MONGODB_URL in .env

### Error: "Redis connection failed"
- **Redis is optional** - backend will work without it
- To disable Redis warnings, the backend already handles this gracefully
- **Use cloud Redis:**
  - Sign up at https://redis.com/try-free/
  - Update REDIS_HOST and REDIS_PORT in .env

### Error: "Address already in use"
```powershell
# Find what's using port 8000
netstat -ano | findstr :8000

# Change port in .env
PORT=8001
```

---

## 🎯 What We're Testing

The backend implements a **GPS-Free positioning system** using cellular towers:

### 1. **Triangulation with Timing Advance** (Best: ~175m accuracy)
   - Uses distance from 3+ towers
   - Requires Timing Advance (TA) data
   - Most accurate method

### 2. **Weighted Centroid** (Good: ~400m accuracy)
   - Uses signal strength (RSSI) from 2+ towers
   - Fallback when TA not available
   - Balances accuracy and reliability

### 3. **Cell-ID Fallback** (Basic: ~800m accuracy)
   - Uses single strongest tower location
   - Last resort method
   - Always works if tower data available

### 4. **Demo Mode** (Perfect: ~50m accuracy)
   - For testing and presentations
   - Uses GPS coordinates from driver app
   - No cellular estimation needed

---

## 📚 Additional Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **MongoDB Tutorial**: https://docs.mongodb.com/manual/tutorial/
- **Redis Tutorial**: https://redis.io/docs/getting-started/
- **OpenCellID**: https://opencellid.org/ (for real tower data)

---

## 🎉 Success Criteria

Your backend is **COMPLETE** when:

1. ✅ All dependencies installed
2. ✅ MongoDB connected
3. ✅ Redis connected (optional)
4. ✅ Backend starts successfully
5. ✅ All 8 tests pass
6. ✅ Position estimation works (test all 3 methods)
7. ✅ API documentation accessible
8. ✅ Can integrate with driver app

---

## 📞 Next Steps After Backend Testing

Once backend is verified:

1. **Test Integration with Driver App**
   - Start backend
   - Start driver app (APPLICATION1-driver-app)
   - Enable tracking in driver app
   - Watch backend receive position updates

2. **Build Commuter App (APPLICATION 2)**
   - Create React Native app for passengers
   - Show real-time bus locations on map
   - Calculate ETAs
   - Display route information

3. **Deploy to Production**
   - Choose cloud provider (AWS, Azure, GCP)
   - Deploy MongoDB (or use Atlas)
   - Deploy Redis (or use Redis Cloud)
   - Deploy FastAPI backend
   - Configure domain and SSL

---

Good luck! 🚀
