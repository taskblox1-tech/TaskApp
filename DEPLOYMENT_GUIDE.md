# Family Task Tracker - Render.com Deployment Guide

## Current Status
✅ CSS file created at `static/css/main.css`
⏳ Need to implement remaining changes

## Files to Create/Update

### 1. requirements.txt
Create at project root with:
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
jinja2==3.1.2
pydantic==2.5.0
pydantic-settings==2.1.0
```

### 2. render.yaml
Create at project root:
```yaml
services:
  - type: web
    name: family-task-tracker
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: family-tasks-db
          property: connectionString
      - key: SECRET_KEY
        generateValue: true
      - key: ENVIRONMENT
        value: production

databases:
  - name: family-tasks-db
    databaseName: family_tasks
    user: family_tasks_user
```

### 3. Update app/config.py
Add environment variable support for Render:
```python
from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/family_tasks")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days
    
    # App
    APP_NAME: str = "Family Task Tracker"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    CORS_ORIGINS: list = ["*"]
    
    model_config = SettingsConfigDict(env_file=".env", extra="allow")
```

## Deployment Steps

### Step 1: Push to GitHub
1. Initialize git repo: `git init`
2. Add files: `git add .`
3. Commit: `git commit -m "Initial commit"`
4. Push to GitHub

### Step 2: Create Render Services
1. Go to dashboard.render.com
2. Click "New +" → "Blueprint"
3. Connect your GitHub repo
4. Render will automatically detect render.yaml
5. Click "Apply" to create services

### Step 3: Database Setup
1. Render creates PostgreSQL automatically
2. Wait for database to be ready
3. Web service will auto-deploy once DB is ready

### Step 4: Run Migrations
In Render shell:
```bash
python -c "from app.database import Base, engine; Base.metadata.create_all(bind=engine)"
```

### Step 5: Create Initial Data
```python
python -c "
from app.database import SessionLocal
from app.models.family import Family
from app.models.profile import Profile
from app.core.security import get_password_hash

db = SessionLocal()

# Create family
family = Family(name='Test Family')
db.add(family)
db.commit()

# Create parent user
parent = Profile(
    family_id=family.id,
    email='parent@example.com',
    password_hash=get_password_hash('password123'),
    first_name='Parent',
    last_name='User',
    role='admin'
)
db.add(parent)
db.commit()
"
```

## Environment Variables in Render
- DATABASE_URL: Auto-set by Render from PostgreSQL
- SECRET_KEY: Auto-generated
- ENVIRONMENT: Set to "production"

## Post-Deployment
1. Access your app at: `https://family-task-tracker.onrender.com`
2. Login with the parent account created
3. Create children and assign tasks

## Notes
- Free tier: Service sleeps after 15 min inactivity
- Paid tier: Always on, faster performance
- Database: 90-day retention on free tier
