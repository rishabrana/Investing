# Deployment Guide

## Vercel Deployment (Frontend Only)

This project is configured to deploy the frontend to Vercel while the backend runs separately.

### Quick Deploy

1. **Push your code to GitHub** (already done!)
   ```bash
   git push origin feature/api-integration
   ```

2. **Import project in Vercel**
   - Go to [vercel.com](https://vercel.com)
   - Click "Add New Project"
   - Import your GitHub repository: `rishabrana/Investing`
   - Vercel will automatically detect the `vercel.json` configuration

3. **Configure Environment Variables in Vercel**
   - In your Vercel project settings, go to "Environment Variables"
   - Add the following variable:
     - **Name**: `VITE_API_BASE_URL`
     - **Value**: Your backend API URL (e.g., `https://your-backend.com/api/v1`)
     - **Note**: Leave this empty for now if you haven't deployed the backend yet. The frontend will build successfully but API calls won't work until you set this.

4. **Deploy**
   - Click "Deploy"
   - Vercel will build and deploy your frontend

### Backend Deployment (Required for Full Functionality)

Your frontend needs a backend API to function. You'll need to deploy the FastAPI backend separately. Recommended options:

#### Option 1: Railway (Easiest for Python)
1. Go to [railway.app](https://railway.app)
2. Create a new project from your GitHub repo
3. Set the root directory to `backend`
4. Add environment variables for API keys
5. Railway will auto-detect Python and deploy

#### Option 2: Render
1. Go to [render.com](https://render.com)
2. Create a new Web Service
3. Connect your GitHub repo
4. Set root directory to `backend`
5. Build command: `pip install -r ../requirements.txt`
6. Start command: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`

#### Option 3: Vercel Serverless Functions
- More complex setup, requires converting FastAPI routes to serverless functions
- Not recommended unless you're familiar with serverless

### After Backend Deployment

1. Get your backend URL (e.g., `https://investing-backend.railway.app`)
2. Update the `VITE_API_BASE_URL` environment variable in Vercel
3. Redeploy your frontend in Vercel (it will pick up the new environment variable)

## Local Development

For local development, the frontend expects the backend to run on `http://localhost:8000`:

```bash
# Terminal 1: Start backend
python -m uvicorn backend.api.main:app --reload --port 8000

# Terminal 2: Start frontend
cd frontend
npm run dev
```

The frontend will use the `VITE_API_BASE_URL` from `frontend/.env.local` (defaults to `http://localhost:8000/api/v1`).
