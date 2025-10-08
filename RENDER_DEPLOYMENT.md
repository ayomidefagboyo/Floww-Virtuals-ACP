# Render Deployment Guide

## Prerequisites
- GitHub account with this repository
- Render account (sign up at [render.com](https://render.com))

## Step 1: Deploy Backend

### Option A: Using Blueprint (Recommended)
1. Go to [render.com](https://render.com) and sign in
2. Click **"New"** → **"Blueprint"**
3. Connect your GitHub repository
4. Select the `backend/render.yaml` file
5. Render will automatically detect the configuration

### Option B: Manual Setup
1. Go to [render.com](https://render.com) and click **"New"** → **"Web Service"**
2. Connect your GitHub repository
3. Configure the service:
   - **Name**: `floww-virtuals-backend`
   - **Region**: Oregon (or closest to you)
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Starter ($7/month)

4. Add environment variables (click "Advanced" → "Add Environment Variable"):
   ```
   PYTHON_VERSION=3.9.18
   HOST=0.0.0.0
   DEBUG=false
   LOG_LEVEL=INFO
   PROJECT_NAME=Floww X Virtuals ACP
   VERSION=1.0.0
   DESCRIPTION=AI Trading Agents with Real Market Data
   ```

5. Optional environment variables for enhanced features:
   ```
   ANTHROPIC_API_KEY=your_anthropic_key_here
   BINANCE_API_KEY=your_binance_key_here
   BINANCE_SECRET_KEY=your_binance_secret_here
   ```

6. Click **"Create Web Service"**

7. Wait for deployment (usually 3-5 minutes)

8. Once deployed, copy your backend URL (e.g., `https://floww-virtuals-backend.onrender.com`)

## Step 2: Deploy Frontend

### Option A: Using Blueprint (Recommended)
1. Click **"New"** → **"Blueprint"**
2. Connect your GitHub repository
3. Select the `frontend/render.yaml` file
4. Update the environment variable with your backend URL

### Option B: Manual Setup
1. Click **"New"** → **"Web Service"**
2. Connect your GitHub repository
3. Configure the service:
   - **Name**: `floww-virtuals-frontend`
   - **Region**: Oregon (or closest to you)
   - **Branch**: `main`
   - **Root Directory**: `frontend`
   - **Runtime**: Node
   - **Build Command**: `npm install && npm run build`
   - **Start Command**: `npm start`
   - **Plan**: Starter ($7/month)

4. Add environment variables:
   ```
   NODE_VERSION=18.17.0
   NODE_ENV=production
   NEXT_PUBLIC_API_URL=https://your-backend-url.onrender.com
   ```
   **Important**: Replace `https://your-backend-url.onrender.com` with your actual backend URL from Step 1

5. Click **"Create Web Service"**

6. Wait for deployment (usually 3-5 minutes)

## Step 3: Verify Deployment

1. Visit your frontend URL (e.g., `https://floww-virtuals-frontend.onrender.com`)
2. Test the AI agents:
   - **Yuki Agent**: Click "Find Trades" to scan trading pairs
   - **Ryu Agent**: Enter a token symbol (e.g., BTC) for analysis
   - **Sakura Agent**: Click "Get Yield Opportunities" for DeFi strategies

## Step 4: Configure CORS (If Needed)

If you encounter CORS errors, update the backend CORS settings:

1. Go to your backend service on Render
2. Add environment variable:
   ```
   ALLOWED_ORIGINS=https://your-frontend-url.onrender.com
   ```

## Troubleshooting

### Backend Issues
- **Build fails**: Check that Python version is 3.9+
- **Health check fails**: Ensure `/health` endpoint is working
- **Import errors**: Verify all dependencies in `requirements.txt`

### Frontend Issues
- **Build fails**: Check Node version is 18+
- **API connection fails**: Verify `NEXT_PUBLIC_API_URL` is correct
- **Environment variables not working**: Ensure they start with `NEXT_PUBLIC_`

### Common Issues
1. **Free tier sleep**: Render free tier services sleep after inactivity. Upgrade to Starter plan for always-on services.
2. **Build timeout**: Increase build timeout in Render settings if needed
3. **Memory issues**: Upgrade plan if services run out of memory

## Auto-Deploy on Git Push

Render automatically deploys when you push to your connected branch (usually `main`). To disable:
1. Go to service settings
2. Under "Auto-Deploy" toggle it off

## Cost Summary

| Service | Plan | Cost |
|---------|------|------|
| Backend | Starter | $7/month |
| Frontend | Starter | $7/month |
| **Total** | | **$14/month** |

### Free Tier Option
Both services can run on free tier with limitations:
- Services sleep after 15 minutes of inactivity
- 750 hours/month of runtime
- Slower cold starts

## Post-Deployment Updates

### Update Environment Variables
1. Go to service dashboard
2. Click "Environment"
3. Add/update variables
4. Service will automatically redeploy

### Manual Redeploy
1. Go to service dashboard
2. Click "Manual Deploy"
3. Select "Clear build cache & deploy" if needed

## Monitoring

- **Logs**: Available in service dashboard under "Logs" tab
- **Metrics**: View CPU, memory, and bandwidth usage
- **Alerts**: Set up email alerts for service health

## Next Steps

1. Set up custom domain (optional)
2. Configure database if needed
3. Set up monitoring and alerts
4. Review and optimize performance

## Support

- Render Documentation: [render.com/docs](https://render.com/docs)
- Render Community: [community.render.com](https://community.render.com)
