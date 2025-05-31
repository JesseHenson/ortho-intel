# 🚀 Ortho Intel Deployment Guide

Deploy your orthopedic competitive intelligence platform for demos to marketing firms and investors.

## 📋 Overview

- **Frontend**: React app (Vite) - Deploy to Vercel (Free)
- **Backend**: FastAPI Python app - Deploy to Railway (Free tier)
- **Total Cost**: Free for demos, ~$5/month for production

## 🔧 Prerequisites

1. GitHub account
2. Vercel account (free) - [Sign up](https://vercel.com)
3. Railway account (free) - [Sign up](https://railway.app)

## 🖥️ Backend Deployment (Railway)

### Step 1: Prepare Backend for Deployment

1. **Create railway.json in project root:**
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn src.backend.api.fastapi_server:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/health"
  }
}
```

2. **Create requirements.txt in project root:**
```txt
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
python-multipart>=0.0.6
pydantic>=2.4.0
httpx>=0.25.0
python-dotenv>=1.0.0
# Add your other backend dependencies
```

### Step 2: Deploy to Railway

1. **Connect GitHub Repository:**
   - Go to [Railway Dashboard](https://railway.app/dashboard)
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your `ortho-intel` repository

2. **Configure Environment Variables:**
   ```
   PORT=8000
   ANTHROPIC_API_KEY=your_anthropic_key
   PERPLEXITY_API_KEY=your_perplexity_key
   OPENAI_API_KEY=your_openai_key
   # Add other API keys as needed
   ```

3. **Set Build Configuration:**
   - Railway should auto-detect Python
   - Start command: `uvicorn src.backend.api.fastapi_server:app --host 0.0.0.0 --port $PORT`
   - Health check: `/health`

4. **Deploy:**
   - Railway will automatically deploy
   - Get your backend URL: `https://your-app-name.railway.app`

## 🌐 Frontend Deployment (Vercel)

### Step 1: Configure Frontend for Production

1. **Create vercel.json in src/frontend-react/:**
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "installCommand": "npm install --legacy-peer-deps"
}
```

2. **Update API URL:**
   - Copy `src/frontend-react/.env.example` to `src/frontend-react/.env.production`
   - Update with your Railway backend URL:
   ```
   VITE_API_BASE_URL=https://your-backend-app.railway.app
   ```

### Step 2: Deploy to Vercel

1. **Connect GitHub:**
   - Go to [Vercel Dashboard](https://vercel.com/dashboard)
   - Click "Add New..." → "Project"
   - Import your GitHub repository

2. **Configure Build Settings:**
   - Framework Preset: `Vite`
   - Root Directory: `src/frontend-react`
   - Build Command: `npm run build`
   - Output Directory: `dist`
   - Install Command: `npm install --legacy-peer-deps`

3. **Add Environment Variables:**
   ```
   VITE_API_BASE_URL=https://your-backend-app.railway.app
   ```

4. **Deploy:**
   - Click "Deploy"
   - Get your frontend URL: `https://your-app-name.vercel.app`

## 🔒 CORS Configuration

Update your FastAPI backend to allow your Vercel domain:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Local development
        "https://your-app-name.vercel.app",  # Production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 🎯 Demo URLs

After deployment, you'll have:
- **Frontend**: `https://your-app-name.vercel.app`
- **Backend API**: `https://your-backend-app.railway.app`
- **API Docs**: `https://your-backend-app.railway.app/docs`

## 💡 Pro Tips for Investor Demos

1. **Custom Domain (Optional):**
   - Vercel allows custom domains on free tier
   - Use something like `ortho-intel-demo.com`

2. **Demo Data:**
   - Pre-populate with sample analyses
   - Use realistic competitor names (Stryker, Zimmer Biomet, etc.)

3. **Performance:**
   - Vercel automatically optimizes React apps
   - Railway handles backend scaling

4. **Monitoring:**
   - Both platforms provide basic analytics
   - Monitor API usage on Railway dashboard

## 🚀 Alternative Free Options

### Netlify + Render (100% Free)
- **Frontend**: Netlify (free forever)
- **Backend**: Render (free tier, 750 hours/month)
- **Limitation**: Render free tier spins down after inactivity

### GitHub Pages + Railway
- **Frontend**: GitHub Pages (free, static hosting)
- **Backend**: Railway (free tier)
- **Limitation**: GitHub Pages only serves static sites

## 📞 Support

If you encounter issues:
1. Check Railway logs for backend errors
2. Check Vercel deployment logs for frontend issues
3. Ensure CORS is properly configured
4. Verify environment variables are set correctly

---

**Estimated Setup Time**: 30-45 minutes
**Monthly Cost**: Free for demos, ~$5-10/month for production use 