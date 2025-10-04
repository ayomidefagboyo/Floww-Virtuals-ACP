# Deployment Guide

## Option 1: Vercel + Railway (Recommended - Cheapest)

### Frontend (Vercel) - FREE
1. Go to [vercel.com](https://vercel.com)
2. Sign up with GitHub
3. Import your repository
4. Set build settings:
   - Framework: Next.js
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `.next`

### Backend (Railway) - $5/month
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Create new project from GitHub repo
4. Select the `backend` folder
5. Railway will auto-detect Python and install dependencies
6. Add environment variables (see below)

### Environment Variables

#### Backend (Railway)
```
ANTHROPIC_API_KEY=your_anthropic_key
BINANCE_API_KEY=your_binance_key
BINANCE_SECRET_KEY=your_binance_secret
PENDLE_API_KEY=your_pendle_key
```

#### Frontend (Vercel)
```
NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app
```

## Option 2: Render (All-in-one) - $7/month

### Frontend on Render
1. Go to [render.com](https://render.com)
2. Create new Web Service
3. Connect GitHub repo
4. Settings:
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Publish Directory: `.next`
   - Environment: Node

### Backend on Render
1. Create new Web Service
2. Connect GitHub repo
3. Settings:
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Environment: Python

## Post-Deployment

1. Update `frontend/vercel.json` with your actual backend URL
2. Test both services are running
3. Update CORS settings if needed

## Cost Comparison

| Option | Frontend | Backend | Total/Month |
|--------|----------|---------|-------------|
| Vercel + Railway | FREE | $5 | $5 |
| Render | $7 | $7 | $14 |
| Vercel + Render | FREE | $7 | $7 |

**Recommendation**: Vercel + Railway for cheapest option
