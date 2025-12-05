# 🗄️ MongoDB Atlas Setup Guide (5 Minutes)

MongoDB Atlas is a **free cloud database** - perfect for development and testing!

---

## 📋 Step-by-Step Setup

### Step 1: Create Account (1 minute)

1. Go to: **https://www.mongodb.com/cloud/atlas/register**
2. Sign up with:
   - Email + Password, OR
   - Google account, OR
   - GitHub account
3. Complete verification

### Step 2: Create Free Cluster (3 minutes)

1. After login, click **"Build a Database"** (or **"Create"**)

2. Choose **"M0 FREE"** tier
   - ✅ 512 MB storage (plenty for testing)
   - ✅ Shared RAM
   - ✅ Free forever
   - ✅ No credit card required

3. Select cloud provider and region:
   - **Provider**: AWS (recommended)
   - **Region**: Choose closest to you
     - US East (N. Virginia) - `us-east-1`
     - US West (Oregon) - `us-west-2`
     - Europe (Ireland) - `eu-west-1`
   - Click **"Create"**

4. Wait 3-5 minutes for cluster to deploy
   - You'll see "Cluster0" being created
   - Status will change to "Active" when ready

### Step 3: Configure Network Access (30 seconds)

1. Click **"Network Access"** in left sidebar
2. Click **"Add IP Address"**
3. Click **"Allow Access from Anywhere"** (for development)
   - This adds `0.0.0.0/0` to whitelist
   - **Note**: For production, use specific IPs
4. Click **"Confirm"**

### Step 4: Create Database User (30 seconds)

1. Click **"Database Access"** in left sidebar
2. Click **"Add New Database User"**
3. Choose **"Password"** authentication
4. Enter:
   - **Username**: `vehicletrack_user` (or any name)
   - **Password**: Click "Autogenerate Secure Password" (or create your own)
   - **IMPORTANT**: Copy/save the password!
5. Set privileges: **"Atlas admin"** or **"Read and write to any database"**
6. Click **"Add User"**

### Step 5: Get Connection String (1 minute)

1. Click **"Database"** in left sidebar
2. Click **"Connect"** button on your cluster (Cluster0)
3. Choose **"Connect your application"**
4. Select:
   - **Driver**: Python
   - **Version**: 3.12 or later
5. Copy the connection string - it looks like:
   ```
   mongodb+srv://vehicletrack_user:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```

6. **Replace `<password>`** with your actual password:
   ```
   mongodb+srv://vehicletrack_user:YourActualPassword123@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```

### Step 6: Update Backend Configuration (30 seconds)

1. Open `backend/.env` file

2. Update the `MONGODB_URL` line:
   ```env
   MONGODB_URL=mongodb+srv://vehicletrack_user:YourActualPassword123@cluster0.xxxxx.mongodb.net/vehicle_tracking
   ```

3. **Add database name** at the end: `/vehicle_tracking`

4. Save the file

---

## ✅ Verify Connection

Run the test script:

```powershell
cd backend
python tmp_rovodev_test_mongodb.py
```

**Expected output:**
```
============================================================
🎉 ALL MONGODB TESTS PASSED!
============================================================

✅ MongoDB is connected and working correctly
✅ Backend can use MongoDB for storage
```

---

## 🚀 Start Backend

Once MongoDB is connected:

```powershell
cd backend
python main.py
```

**Expected output:**
```
INFO:     Connected to MongoDB successfully
INFO:     Connected to Redis successfully at redis-16925...
INFO:     Backend started successfully!
INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

## 🧪 Run Full Test Suite

In a new terminal:

```powershell
cd backend
python tmp_rovodev_test_backend.py
```

**Expected output:**
```
🎉 ALL TESTS PASSED!
```

---

## 📊 View Your Data in Atlas

1. Go to **"Database"** in Atlas dashboard
2. Click **"Browse Collections"** on your cluster
3. Select **"vehicle_tracking"** database
4. View collections:
   - `positions` - Vehicle position updates
   - `vehicles` - Registered vehicles
   - `routes` - Bus routes
   - `towers` - Cell tower locations

---

## 🔒 Security Best Practices

### For Development (Current Setup)
- ✅ Allow access from anywhere (0.0.0.0/0)
- ✅ Use strong password

### For Production (Later)
- ⚠️ Restrict IP addresses to your server IPs only
- ⚠️ Use separate user with minimal permissions
- ⚠️ Enable MongoDB Atlas backup
- ⚠️ Enable audit logs

---

## 💡 Tips

### Connection String Format
```
mongodb+srv://username:password@host/database?options
```

Parts:
- `username` - Database user (not Atlas account)
- `password` - User password (URL-encoded if special chars)
- `host` - Cluster hostname (e.g., cluster0.xxxxx.mongodb.net)
- `database` - Database name (e.g., vehicle_tracking)
- `options` - Connection options (retryWrites, w, etc.)

### Password with Special Characters
If password has special characters, URL-encode them:
- `@` → `%40`
- `:` → `%3A`
- `/` → `%2F`
- `?` → `%3F`
- `#` → `%23`

Example:
- Password: `P@ss:word/123`
- Encoded: `P%40ss%3Aword%2F123`

### Test Connection in Atlas
1. Go to **"Database"** → Click **"Connect"**
2. Choose **"Connect with MongoDB Compass"** (GUI tool)
3. Download Compass (optional)
4. Use connection string to verify it works

---

## 🐛 Troubleshooting

### Error: "Authentication failed"
- ✅ Check username is correct
- ✅ Check password is correct (and URL-encoded if needed)
- ✅ Wait 2-3 minutes after creating user (propagation delay)

### Error: "IP not whitelisted"
- ✅ Add `0.0.0.0/0` in Network Access
- ✅ Wait 1-2 minutes after adding IP

### Error: "Connection timeout"
- ✅ Check your internet connection
- ✅ Check firewall allows MongoDB (port 27017)
- ✅ Try different network (corporate networks may block)

### Error: "Database not found"
- ✅ This is OK! Database is created automatically on first insert
- ✅ Just make sure connection string ends with `/vehicle_tracking`

---

## 📈 MongoDB Atlas Free Tier Limits

| Resource | Limit |
|----------|-------|
| Storage | 512 MB |
| RAM | Shared |
| Connections | 500 concurrent |
| Backup | No auto-backup |
| Clusters | 1 per project |

**Perfect for:**
- ✅ Development
- ✅ Testing
- ✅ Small applications
- ✅ Prototypes
- ✅ Learning

**Upgrade when you need:**
- More storage (>512 MB)
- Dedicated resources
- Automatic backups
- Production workloads

---

## 🎯 Next Steps After Setup

Once MongoDB Atlas is connected:

1. ✅ Run `python tmp_rovodev_test_mongodb.py` - Verify connection
2. ✅ Run `python main.py` - Start backend
3. ✅ Run `python tmp_rovodev_test_backend.py` - Run full test suite
4. ✅ Visit http://localhost:8000/docs - Interactive API docs
5. ✅ Test driver app integration
6. ✅ Build commuter app (APPLICATION 2)

---

## 📞 Need Help?

If you have issues:

1. **Check cluster status** - Should be "Active" in Atlas
2. **Test with MongoDB Compass** - Verify connection string works
3. **Check Network Access** - IP whitelist includes 0.0.0.0/0
4. **Check Database Access** - User has correct permissions
5. **Wait a few minutes** - Changes take time to propagate

---

## 🎉 Summary

**What you're getting:**
- ✅ Free forever MongoDB database
- ✅ 512 MB storage (enough for thousands of position updates)
- ✅ Global CDN with low latency
- ✅ Automatic scaling
- ✅ No credit card required
- ✅ Works from anywhere

**Setup time:** 5-10 minutes

**Once done, your backend will be fully functional!** 🚀

---

**Ready to set up? Follow the steps above, then paste your MongoDB connection string here!**
