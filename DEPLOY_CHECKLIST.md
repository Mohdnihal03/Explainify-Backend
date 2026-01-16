# Quick Start - Render Deployment Checklist

## ✅ Pre-Deployment Checklist

- [ ] Code is working locally
- [ ] All dependencies are in `requirements.txt`
- [ ] `.env` file is in `.gitignore`
- [ ] Code is pushed to GitHub

## 📝 Deployment Steps

### 1️⃣ Create PostgreSQL Database
1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **New +** → **PostgreSQL**
3. Name: `explainify-db`
4. Plan: **Free**
5. Click **Create Database**
6. **Save the Internal Database URL** (you'll need it)

### 2️⃣ Create Web Service
1. Click **New +** → **Web Service**
2. Connect your GitHub repo: `Explainify-Backend`
3. Fill in:
   - **Name**: `explainify-backend`
   - **Branch**: `main`
   - **Build Command**: `cd Backend && chmod +x build.sh && ./build.sh`
   - **Start Command**: `cd Backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: **Free**

### 3️⃣ Add Environment Variables
Click **Add Environment Variable** for each:

| Key | Value |
|-----|-------|
| `PYTHON_VERSION` | `3.11.0` |
| `GOOGLE_API_KEY` | Your actual Google API key |
| `SECRET_KEY` | Click "Generate" button |
| `DATABASE_URL` | Click "Add from database" → Select `explainify-db` |
| `ALLOWED_ORIGINS` | `*` (update later with frontend URL) |

### 4️⃣ Deploy
1. Click **Create Web Service**
2. Wait 5-10 minutes for deployment
3. Your API will be live at: `https://explainify-backend.onrender.com`

## ✅ Verify Deployment

Test your API:
```bash
# Health check
curl https://explainify-backend.onrender.com/health

# Test transcript endpoint
curl -X POST https://explainify-backend.onrender.com/transcript \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'
```

## 🎯 What's Next?

- Update `ALLOWED_ORIGINS` with your frontend URL
- Monitor logs in Render dashboard
- Set up custom domain (optional)

## 📚 Full Guide

For detailed instructions and troubleshooting, see [RENDER_DEPLOYMENT_GUIDE.md](file:///C:/Users/moham/.gemini/antigravity/brain/d3b47be8-79af-4b44-bd5b-5c033e152d01/RENDER_DEPLOYMENT_GUIDE.md)

## ⚠️ Important Notes

- **Free tier spins down after 15 min** of inactivity (first request takes 30-60s)
- **Database expires after 90 days** on free tier
- **Never commit `.env` file** to GitHub
- **Update CORS origins** after deploying frontend
