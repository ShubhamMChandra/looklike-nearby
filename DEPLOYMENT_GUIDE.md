# 🚀 Deployment Guide: Vercel Frontend + Railway Backend

This guide shows you how to deploy the **LookLike Nearby** lead generation platform using **Vercel for the frontend** and **Railway for the backend**.

## 🏗️ Architecture Overview

```
┌─────────────────┐    API Calls    ┌─────────────────┐
│                 │ ──────────────► │                 │
│  Vercel         │                 │  Railway        │
│  (Next.js)      │                 │  (FastAPI)      │
│  Frontend       │ ◄────────────── │  Backend        │
│                 │    Responses    │                 │
└─────────────────┘                 └─────────────────┘
                                              │
                                              ▼
                                    ┌─────────────────┐
                                    │   PostgreSQL    │
                                    │   Database      │
                                    └─────────────────┘
```

## 📋 Prerequisites

- GitHub account
- Vercel account (free)
- Railway account (free tier available)
- Google Maps Platform API key

---

## 🚄 Step 1: Deploy Backend to Railway

### 1.1 Create Railway Project

1. Go to [Railway](https://railway.app)
2. **Sign in** with GitHub
3. Click **"New Project"**
4. Select **"Deploy from GitHub repo"**
5. Choose: `ShubhamMChandra/looklike-nearby`

### 1.2 Add PostgreSQL Database

1. In Railway dashboard, click **"Add Service"**
2. Select **"PostgreSQL"**
3. Railway will automatically create `DATABASE_URL`

### 1.3 Configure Environment Variables

In Railway → **Variables**, add:

```bash
# Required
GOOGLE_API_KEY=your-google-maps-api-key-here
APP_PASSWORD=your-secure-password-here

# Optional
DEBUG=false
FRONTEND_URL=https://your-app.vercel.app
```

### 1.4 Deploy Backend

1. Railway should automatically detect Python and deploy
2. Wait for deployment to complete
3. Note your Railway URL: `https://your-app.railway.app`
4. Test health check: `https://your-app.railway.app/health`

---

## ⚡ Step 2: Deploy Frontend to Vercel

### 2.1 Create Vercel Project

1. Go to [Vercel](https://vercel.com)
2. **Sign in** with GitHub
3. Click **"New Project"**
4. **Import** your GitHub repo: `ShubhamMChandra/looklike-nearby`

### 2.2 Configure Project Settings

**Framework Preset**: Next.js
**Root Directory**: `frontend-nextjs`
**Build Command**: `npm run build`
**Output Directory**: `.next`

### 2.3 Set Environment Variables

In Vercel → **Settings** → **Environment Variables**:

```bash
NEXT_PUBLIC_API_URL=https://your-app.railway.app
```

Replace `your-app.railway.app` with your actual Railway URL.

### 2.4 Deploy Frontend

1. Click **"Deploy"**
2. Vercel will build and deploy automatically
3. Your app will be available at: `https://your-app.vercel.app`

---

## 🔧 Step 3: Configure Cross-Origin Access

### 3.1 Update Railway Environment

Add your Vercel URL to Railway environment variables:

```bash
FRONTEND_URL=https://your-app.vercel.app
```

### 3.2 CORS Configuration

The backend is already configured to accept requests from:
- `http://localhost:3000` (development)
- `https://*.vercel.app` (Vercel deployments)
- Your custom `FRONTEND_URL`

---

## 🧪 Step 4: Test the Integration

### 4.1 Test Backend API

```bash
curl https://your-app.railway.app/health
# Should return: {"status": "healthy", "service": "looklike-nearby"}
```

### 4.2 Test Frontend

1. Visit: `https://your-app.vercel.app`
2. Login with your `APP_PASSWORD`
3. Try searching for businesses
4. Check browser dev tools for any CORS errors

---

## 🔄 Step 5: Development Workflow

### 5.1 Local Development

**Backend (Railway)**:
```bash
# Run locally
python run.py

# API available at: http://localhost:8000
```

**Frontend (Vercel)**:
```bash
cd frontend-nextjs
npm install
npm run dev

# App available at: http://localhost:3000
```

### 5.2 Environment Variables for Local Development

**Backend** (`.env`):
```bash
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/db
GOOGLE_API_KEY=your-key
APP_PASSWORD=airfare
DEBUG=true
```

**Frontend** (`frontend-nextjs/.env.local`):
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 🎯 Step 6: Access Your Application

### Production URLs:
- **Frontend**: `https://your-app.vercel.app`
- **Backend API**: `https://your-app.railway.app`
- **API Docs**: `https://your-app.railway.app/docs`

### Default Login:
- **Password**: Value of `APP_PASSWORD` environment variable

---

## 🔧 Troubleshooting

### CORS Issues
```bash
# Check CORS headers
curl -H "Origin: https://your-app.vercel.app" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: X-Requested-With" \
     -X OPTIONS \
     https://your-app.railway.app/api/auth/login
```

### Database Connection Issues
1. Check Railway PostgreSQL service is running
2. Verify `DATABASE_URL` environment variable
3. Check Railway logs for connection errors

### API Integration Issues
1. Verify `NEXT_PUBLIC_API_URL` in Vercel
2. Check browser Network tab for failed requests
3. Ensure Railway backend is responding to health checks

---

## 🚀 Benefits of This Architecture

✅ **Scalable**: Vercel handles frontend scaling, Railway handles backend
✅ **Fast**: Vercel CDN for frontend, Railway for API performance  
✅ **Cost-effective**: Both platforms have generous free tiers
✅ **Easy deployment**: Git-based deployments with automatic builds
✅ **Secure**: Environment variables, HTTPS by default
✅ **Developer-friendly**: Hot reloading, instant deployments

---

## 📈 Next Steps

1. **Custom Domain**: Add your domain to Vercel
2. **Monitoring**: Set up Railway metrics and Vercel analytics
3. **CI/CD**: Configure automated testing and deployment
4. **Performance**: Optimize with caching and image optimization
5. **Features**: Add the remaining features from the roadmap

**Your B2B lead generation platform is now live! 🎉**
