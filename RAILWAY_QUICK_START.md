# 🚂 Railway Quick Start - 5 Steps

## ⚡ Deploy in 10 Minutes

### Step 1: Sign Up (2 min)
1. Go to: **https://railway.app/**
2. Click **"Login with GitHub"**
3. Authorize Railway
4. Get $5 free credit automatically!

---

### Step 2: Deploy from GitHub (1 min)
1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose: **Tracking_app_backend**
4. Railway starts building automatically

---

### Step 3: Add Environment Variables (3 min)

Click your service → **"Variables"** tab → **"+ New Variable"**

**Add these 9 variables:**

```
MONGODB_URL
mongodb+srv://twitter7817_db_user:0AhdcaXftl1A1Ywu@cluster0.vstmjjk.mongodb.net/vehicle_tracking?appName=Cluster0

MONGODB_DB_NAME
vehicle_tracking

REDIS_HOST
redis-16925.c8.us-east-1-4.ec2.cloud.redislabs.com

REDIS_PORT
16925

REDIS_PASSWORD
aBUfustcyLCHpW1tLObInekWJQDsa8Q5

REDIS_DB
0

DEBUG
false

CORS_ORIGINS
["*"]

PORT
8000
```

Railway auto-redeploys after adding variables!

---

### Step 4: Generate Public URL (1 min)
1. Go to **"Settings"** tab
2. Scroll to **"Domains"**
3. Click **"Generate Domain"**
4. Copy your URL: `https://tracking-app-backend-production.up.railway.app`

---

### Step 5: Test (2 min)

**Open in browser:**
```
https://your-app.up.railway.app/health
```

**Expected:**
```json
{"status":"healthy","mongodb":true,"redis":true}
```

**API Docs:**
```
https://your-app.up.railway.app/docs
```

---

## ✅ Success!

Your backend is now:
- ✅ Live on Railway
- ✅ Connected to MongoDB Atlas
- ✅ Connected to Redis Cloud
- ✅ Accessible from anywhere
- ✅ Auto-deploys from GitHub

---

## 📱 Next: Update Driver App

Edit `APPLICATION1-driver-app/src/config/api.js`:

```javascript
BASE_URL: 'https://your-app.up.railway.app',
```

---

## 🎯 Important Notes

- **No Sleep**: Railway doesn't sleep (unlike Render)
- **Fast**: First request is instant
- **Credit**: $5 free (~500 hours)
- **Logs**: Real-time in "Deployments" tab
- **Auto-deploy**: Push to GitHub = auto-deploy

---

## 📞 Need Help?

Full guide: `backend/RAILWAY_DEPLOYMENT_GUIDE.md`

Docs: https://docs.railway.app/

---

**Go to https://railway.app/ and start deploying!** 🚀
