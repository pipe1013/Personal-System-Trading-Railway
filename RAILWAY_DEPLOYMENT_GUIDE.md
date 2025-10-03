# Railway Deployment Guide - Trading System

## ✅ What We've Set Up

Your Flask trading system has been configured for Railway deployment with the following changes:

1. **config.py** - Environment-specific database paths
2. **app.py** - Production-ready configuration with database initialization
3. **Procfile** - WSGI server configuration 
4. **railway.json** - Railway deployment configuration
5. **requirements.txt** - Optimized dependencies for Railway
6. **.railwayignore** - Excludes unnecessary files from deployment

## 🚀 Step-by-Step Deployment

### Step 1: Install Railway CLI

**Option A: npm (Recommended)**
```bash
npm install -g @railway/cli
```

**Option B: Direct Download**
- Visit https://railway.app/download
- Download the installer for Windows/Mac/Linux

### Step 2: Login to Railway

```bash
railway login
```

### Step 3: Initialize Railway Project

```bash
# Navigate to your project directory
cd C:\Users\NGEICH\Documents\Repositorios\Personal-System-Trading-Railway

# Initialize Railway
railway init
```

### Step 4: Deploy Your Application

```bash
# Deploy to Railway
railway up
```

This command will:
- Build your Python application
- Install all dependencies
- Start your Flask app with Gunicorn

### Step 5: Set Environment Variables

In the Railway dashboard:

1. Go to your project
2. Click on "Variables" tab
3. Add these environment variables:

```
SECRET_KEY = your_very_secure_secret_key_change_this_to_something_random
RAILWAY_ENVIRONMENT = production
DB_PATH = /tmp/trading_system.db
```

**Generate a strong SECRET_KEY:**
You can use this Python code to generate a secure key:
```python
import secrets
print(secrets.token_hex(32))
```

### Step 6: Access Your Application

After deployment, Railway will provide you with:
- **Temporary URL**: `https://your-project-name-randomstring.railway.app`
- **Domain**: You can set up a custom domain in Railway dashboard

## 🔧 Configuration Details

### Environment Variables Explained

- **SECRET_KEY**: Used by Flask for session management (REQUIRED for security)
- **RAILWAY_ENVIRONMENT**: Tells your app it's running in production
- **DB_PATH**: SQLite database location in Railway's filesystem

### Database Persistence

⚠️ **Important**: Railway has ephemeral file systems. Your SQLite database will persist for your session but may be reset when Railway restarts your service.

**For production**: Consider upgrading to Railway PostgreSQL for permanent data storage.

### Custom Domain Setup

1. In Railway dashboard → Settings → Domains
2. Add your custom domain
3. Follow DNS configuration instructions

## 📊 Monitoring Your Application

### Health Check
Your app responds to: `https://your-url.railway.app`
Login page: `https://your-url.railway.app/login`

### Logs
View logs in Railway dashboard or with CLI:
```bash
railway logs
```

### Resource Usage
Monitor CPU/Memory usage in Railway dashboard

## 🛠️ Troubleshooting

### Common Issues

1. **Build Fails**
   - Check `requirements.txt` for problematic packages
   - Ensure all dependencies are compatible

2. **App Won't Start**
   - Check environment variables are set correctly
   - Verify PORT is available (Railway sets this automatically)

3. **Database Errors**
   - Check Rails logs for init_db() errors
   - Verify DB_PATH environment variable

4. **Memory Issues**
   - Monitor RAM usage in Railway dashboard
   - Consider upgrading Railway plan if needed

### Useful Commands

```bash
# Check status
railway status

# View logs
railway logs --tail

# Connect to Railway shell
railway shell

# Redeploy
railway up

# Variables management
railway variables
```

## 🔐 Security Best Practices

1. **Strong Secret Key**: Always use a strong, random SECRET_KEY
2. **Environment Variables**: Never commit secrets to code
3. **HTTPS**: Railway provides SSL by default
4. **Database**: For production, use Railway PostgreSQL instead of SQLite

## 📈 Scaling

Railway automatically handles:
- Load balancing
- SSL certificates
- Domain management
- Auto-scaling based on traffic

For increased resources:
1. Go to Railway dashboard
2. Upgrade your plan
3. Configure resource limits

## 🎉 You're Done!

Your Flask trading system is now deployed on Railway! 

- **Local Development**: Use `python app.py` with SQLite in project directory
- **Production**: Access via Railway URL with SQLite in `/tmp/` directory

The app supports all your features:
- User authentication
- Trade registration
- Statistics and analytics
- Trading strategies
- Personal notebooks
- Habit tracking

Access your deployed application at the Railway-provided URL and start trading! 📈
