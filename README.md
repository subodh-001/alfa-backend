# 🌸 Alfa AI Backend - Production Server

Production-ready backend for Alfa anime AI companion app.

## 🚀 Quick Deploy to Render

### Step 1: Create GitHub Repository

1. **Create new repository on GitHub:**
   - Go to [github.com](https://github.com)
   - Click "New repository"
   - Name: `alfa-ai-backend`
   - Make it public
   - Don't initialize with README

2. **Upload this folder to GitHub:**
   ```bash
   cd alfa-backend
   git init
   git add .
   git commit -m "Initial commit - Alfa AI Backend"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/alfa-ai-backend.git
   git push -u origin main
   ```

### Step 2: Deploy on Render

1. **Go to Render:**
   - Visit [render.com](https://render.com)
   - Sign up/Login with GitHub

2. **Create Web Service:**
   - Click "New +" → "Web Service"
   - Connect GitHub account
   - Select `alfa-ai-backend` repository
   - Click "Connect"

3. **Configuration (Auto-detected):**
   - Name: `alfa-ai-backend` (or your choice)
   - Environment: `Python`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn --bind 0.0.0.0:$PORT app:app --workers 2 --timeout 30`
   - Plan: `Free`

4. **Environment Variables (Optional):**
   - Click "Advanced" → "Add Environment Variable"
   - Key: `DEEPSEEK_API_KEY`
   - Value: Your DeepSeek API key (get from deepseek.com)
   - Click "Add"

5. **Deploy:**
   - Click "Create Web Service"
   - Wait 2-3 minutes for deployment

### Step 3: Get Your Live URL

After deployment, you'll get a URL like:
```
https://alfa-ai-backend-xxxx.onrender.com
```

### Step 4: Test Your Backend

Test health endpoint:
```bash
curl https://your-app-name.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "message": "Alfa is ready to help! 💕",
  "timestamp": "2025-12-29T..."
}
```

Test chat endpoint:
```bash
curl -X POST https://your-app-name.onrender.com/ask \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello Alfa!", "user_id": "test"}'
```

## 🔧 API Endpoints

- `GET /` - Home page with server info
- `GET /health` - Health check
- `GET /status` - Detailed server status
- `POST /ask` - Chat with Alfa
- `POST /clear` - Clear conversation history
- `GET /personality` - Get Alfa's personality info

## 💡 Features

✅ **24/7 Uptime** - Render free tier (750 hours/month)
✅ **Auto-scaling** - Handles multiple users
✅ **Health monitoring** - Auto-restart on failures
✅ **Memory management** - Automatic cleanup
✅ **Error handling** - Graceful fallbacks
✅ **CORS enabled** - Works with mobile apps

## 🌟 Production Ready

- Gunicorn WSGI server
- Multiple worker processes
- Request timeouts
- Comprehensive logging
- Memory optimization
- Error recovery

## 🔑 Environment Variables

- `DEEPSEEK_API_KEY` - Optional DeepSeek API key
- `PORT` - Auto-set by Render

## 📊 Monitoring

Check server status:
```
GET /status
```

Returns:
- Uptime
- Request count
- Active conversations
- DeepSeek API status

---

**Your Alfa AI backend is now live 24/7! 🌸✨**