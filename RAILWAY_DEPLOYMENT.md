# 🚀 Railway Deployment Guide - Full ML Pipeline

## 🎯 **Why Railway is Perfect for Your ML App**

- ✅ **No size limits** - Can handle large ML libraries
- ✅ **Fast deployment** - Automatic Python detection
- ✅ **Environment variables** - Easy configuration
- ✅ **Custom domains** - Professional URLs
- ✅ **Auto-scaling** - Handles traffic spikes
- ✅ **Free tier available** - Perfect for hackathons

## 📋 **Step-by-Step Railway Deployment**

### **Step 1: Prepare Your Repository**

Your repository is already ready! Make sure you have:
- ✅ `main.py` (your FastAPI app)
- ✅ `requirements.txt` (all dependencies)
- ✅ `Procfile` (for Railway)
- ✅ All your ML modules

### **Step 2: Deploy to Railway**

1. **Go to [Railway.app](https://railway.app)**
2. **Sign in with GitHub**
3. **Click "New Project"**
4. **Select "Deploy from GitHub repo"**
5. **Choose your repository**: `hackrx-6.0-llm-system`
6. **Railway will automatically detect** it's a Python app
7. **Click "Deploy"**

### **Step 3: Configure Environment Variables**

After deployment, go to your Railway project:

1. **Click on your project**
2. **Go to "Variables" tab**
3. **Add these environment variables**:

```
OPENAI_API_KEY = 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

PINECONE_API_KEY = your_pinecone_api_key_here

PINECONE_ENVIRONMENT = gcp-starter

API_TOKEN = 667efb9a18a1e0cb1dbc77a25fddc98c12849e980fc25cc9dea06eca61b1f4c8
```

4. **Click "Save"**
5. **Railway will automatically redeploy**

### **Step 4: Get Your URL**

1. **Go to "Settings" tab**
2. **Copy your Railway URL** (e.g., `https://your-app-name.railway.app`)
3. **This is your API endpoint!**

### **Step 5: Test Your Deployed API**

Test your Railway deployment:

```bash
# Health check
curl https://your-app-name.railway.app/health

# Main endpoint
curl -X POST "https://your-app-name.railway.app/hackrx/run" \
  -H "Authorization: Bearer 667efb9a18a1e0cb1dbc77a25fddc98c12849e980fc25cc9dea06eca61b1f4c8" \
  -H "Content-Type: application/json" \
  -d '{
    "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
    "questions": [
      "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?"
    ]
  }'
```

### **Step 6: Submit to Hackathon**

1. **Copy your Railway URL**: `https://your-app-name.railway.app`
2. **Go to HackRx 6.0 platform**
3. **Submit your webhook URL**: `https://your-app-name.railway.app/hackrx/run`
4. **Add description**: "FastAPI + GPT-4 + Pinecone vector search with RAG - Full ML Pipeline"
5. **Click "Run" to test**

## 🔧 **Railway Advantages**

### **No Size Limits**
- Railway can handle your full ML pipeline
- No restrictions on library sizes
- All your dependencies will work

### **Automatic Detection**
- Railway automatically detects Python apps
- No complex configuration needed
- Works with your existing `main.py`

### **Environment Variables**
- Easy to configure API keys
- Secure storage of secrets
- No need to modify code

### **Custom Domains**
- Professional URLs
- SSL certificates included
- Perfect for hackathon submissions

## 🚀 **Alternative: Render Deployment**

If Railway doesn't work, try Render:

1. **Go to [Render.com](https://render.com)**
2. **Sign in with GitHub**
3. **Click "New"** → **"Web Service"**
4. **Connect your repository**
5. **Configure:**
   - **Name**: `hackrx-6.0-llm-system`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. **Add environment variables**
7. **Deploy!**

## 🏆 **You're Ready to Win!**

With Railway, you get:
- ✅ **Full ML pipeline** (no compromises)
- ✅ **All dependencies** working
- ✅ **Fast deployment**
- ✅ **Professional URL**
- ✅ **Auto-scaling**
- ✅ **Perfect for hackathons**

**Railway is the best choice for your ML application! 🚀** 