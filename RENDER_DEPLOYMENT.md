# Render.com Deployment Guide

## Pre-Deployment Checklist

### ✅ Files Ready for Deployment

1. **requirements.txt** - All Python dependencies listed
2. **render.yaml** - Render service configuration
3. **.gitignore** - Prevents committing sensitive files (.env, cache, logs)
4. **main.py** - FastAPI application entry point
5. **app/** - Backend code (models, API endpoints, config)
6. **templates/** - HTML templates (Jinja2)
7. **static/** - CSS, JS, images

### ⚠️ Important: DO NOT commit .env file

Your `.env` file contains sensitive credentials and should NEVER be pushed to GitHub. It's now in `.gitignore`.

---

## Step-by-Step Deployment

### 1. Push to GitHub

```bash
cd C:/Users/ArmandLefebvre/family-task-tracker

# Initialize git (if not already done)
git init

# Add all files (except those in .gitignore)
git add .

# Commit
git commit -m "Initial commit for Render deployment"

# Create GitHub repo and push
git remote add origin https://github.com/YOUR_USERNAME/family-task-tracker.git
git branch -M main
git push -u origin main
```

### 2. Create Render Account

1. Go to https://render.com
2. Sign up with your GitHub account
3. Authorize Render to access your repositories

### 3. Create PostgreSQL Database

1. From Render Dashboard, click **"New +"** → **"PostgreSQL"**
2. Configure:
   - **Name**: `family-tasks-db`
   - **Database**: `family_tasks`
   - **User**: `family_tasks_user`
   - **Region**: Choose closest to you
   - **Plan**: Free tier is fine for testing
3. Click **"Create Database"**
4. Wait 2-3 minutes for provisioning
5. **Save the Internal Database URL** (you'll need this)

### 4. Create Web Service

1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository
3. Configure:
   - **Name**: `family-task-tracker`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free tier

### 5. Set Environment Variables

In the **Environment** tab, add these variables:

| Key | Value | Notes |
|-----|-------|-------|
| `DATABASE_URL` | (From PostgreSQL service) | Click "Add from database" |
| `SECRET_KEY` | (Auto-generated) | Click "Generate" |
| `ENVIRONMENT` | `production` | |
| `CORS_ORIGINS` | `*` | Or your specific domain |

**Important**: Render will automatically connect `DATABASE_URL` from your PostgreSQL service.

### 6. Deploy

1. Click **"Create Web Service"**
2. Render will:
   - Clone your repo
   - Install dependencies
   - Start the application
   - Initialize the database
3. Watch the logs for any errors
4. First deployment takes 3-5 minutes

### 7. Access Your Application

Once deployed, your app will be at:
```
https://family-task-tracker.onrender.com
```

---

## Post-Deployment Setup

### Create Initial Data

You need to create:
1. **Family** - A family group
2. **Parent User** - Admin account
3. **Child Users** - Kid accounts
4. **Tasks** - Daily/weekly tasks
5. **Task Assignments** - Assign tasks to children
6. **Rewards** - Point redemption options

You can do this via the `/api/docs` endpoint (Swagger UI) or create a setup script.

### Test the Application

1. **Register** a parent account
2. **Create** a family
3. **Add** children
4. **Create** tasks in the library
5. **Assign** tasks to children
6. **Login** as child
7. **Complete** tasks
8. **Login** as parent
9. **Approve** completed tasks

---

## Monitoring & Logs

- **View Logs**: Render Dashboard → Your Service → Logs
- **Health Check**: `https://your-app.onrender.com/health`
- **API Docs**: `https://your-app.onrender.com/api/docs` (disabled in production)

---

## Troubleshooting

### Database Connection Issues
- Verify `DATABASE_URL` is set correctly
- Check PostgreSQL service is running
- Ensure database user has proper permissions

### Static Files Not Loading
- Verify `/static` folder is in repository
- Check browser console for 404 errors
- Ensure paths are correct in templates

### Authentication Not Working
- Verify `SECRET_KEY` is set
- Check cookie settings (SameSite, secure)
- Ensure CORS_ORIGINS includes your domain

### Template Changes Not Appearing
- In production, templates are cached
- Restart the service to reload templates
- Or redeploy from GitHub

---

## Updating Your App

```bash
# Make changes to your code
git add .
git commit -m "Description of changes"
git push

# Render will automatically detect the push and redeploy
```

---

## Cost

**Free Tier Limits**:
- Web Service: 750 hours/month (enough for 24/7)
- PostgreSQL: 90 days free, then $7/month
- App sleeps after 15 min of inactivity (wakes up on first request)

For production use, consider upgrading to paid tiers for:
- No sleep time
- More resources
- Better performance
