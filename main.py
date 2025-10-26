"""
Family Task Tracker - Complete Python Application
Run with: uvicorn main:app --reload
"""

from fastapi import FastAPI, Request, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, String, Integer, Boolean, Date, DateTime, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from datetime import datetime, date, timedelta
from jose import JWTError, jwt
import secrets
import uvicorn
from typing import Optional, List
import json
import hashlib

# Database Setup
DATABASE_URL = "sqlite:///./family_tasks.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Security
SECRET_KEY = secrets.token_urlsafe(32)
ALGORITHM = "HS256"

# Models
class Family(Base):
    __tablename__ = "families"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    join_code = Column(String, unique=True, nullable=False)
    admin_id = Column(Integer, ForeignKey("users.id"))
    auto_assign_enabled = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    users = relationship("User", back_populates="family", foreign_keys="User.family_id")
    tasks = relationship("Task", back_populates="family", cascade="all, delete-orphan")
    rewards = relationship("Reward", back_populates="family", cascade="all, delete-orphan")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String)
    family_id = Column(Integer, ForeignKey("families.id"))
    role = Column(String, default="child")  # admin, parent, child
    total_lifetime_points = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    family = relationship("Family", back_populates="users", foreign_keys=[family_id])
    assigned_tasks = relationship("TaskAssignment", back_populates="child")
    daily_progress = relationship("DailyProgress", back_populates="child")

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    family_id = Column(Integer, ForeignKey("families.id"))
    title = Column(String, nullable=False)
    points = Column(Integer, default=10)
    icon = Column(String, default="⭐")
    period = Column(String, default="anytime")  # morning, evening, anytime
    category = Column(String, default="daily")  # daily, bonus, general
    day_type = Column(String, default="anyday")  # weekday, weekend, anyday
    created_at = Column(DateTime, default=datetime.utcnow)
    
    family = relationship("Family", back_populates="tasks")
    assignments = relationship("TaskAssignment", back_populates="task", cascade="all, delete-orphan")

class TaskAssignment(Base):
    __tablename__ = "task_assignments"
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"))
    child_id = Column(Integer, ForeignKey("users.id"))
    assigned_at = Column(DateTime, default=datetime.utcnow)
    
    task = relationship("Task", back_populates="assignments")
    child = relationship("User", back_populates="assigned_tasks")

class Reward(Base):
    __tablename__ = "rewards"
    id = Column(Integer, primary_key=True, index=True)
    family_id = Column(Integer, ForeignKey("families.id"))
    name = Column(String, nullable=False)
    cost = Column(Integer, nullable=False)
    icon = Column(String, default="🎁")
    reward_type = Column(String, default="special")  # screen_time, special
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    family = relationship("Family", back_populates="rewards")

class DailyProgress(Base):
    __tablename__ = "daily_progress"
    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("users.id"))
    date = Column(Date, default=date.today)
    total_points = Column(Integer, default=0)
    completed_task_ids = Column(String, default="[]")  # JSON array as string
    redeemed_reward_ids = Column(String, default="[]")  # JSON array as string
    
    child = relationship("User", back_populates="daily_progress")

class CalendarEvent(Base):
    __tablename__ = "calendar_events"
    id = Column(Integer, primary_key=True, index=True)
    family_id = Column(Integer, ForeignKey("families.id"))
    title = Column(String, nullable=False)
    description = Column(String)
    event_date = Column(Date, nullable=False)
    event_time = Column(String)  # Store as string like "14:30"
    event_type = Column(String, default="activity")  # appointment, activity, reminder
    color = Column(String, default="blue")
    created_by = Column(Integer, ForeignKey("users.id"))
    is_completed = Column(Boolean, default=False)
    points_for_completion = Column(Integer, default=15)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    family = relationship("Family")

class WeeklyProgress(Base):
    __tablename__ = "weekly_progress"
    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("users.id"))
    week_start = Column(Date)  # Friday
    week_end = Column(Date)    # Thursday
    total_points = Column(Integer, default=0)
    tasks_completed = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    child = relationship("User")

# Create tables
Base.metadata.create_all(bind=engine)

# FastAPI App
app = FastAPI(title="Family Task Tracker")
templates = Jinja2Templates(directory="templates")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(request: Request, db: Session = Depends(get_db)) -> Optional[User]:
    token = request.cookies.get("session_token")
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        return db.query(User).filter(User.id == user_id).first()
    except JWTError:
        return None

def create_session_token(user_id: int) -> str:
    payload = {"user_id": user_id}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

# Helper Functions
def generate_join_code() -> str:
    chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    return ''.join(secrets.choice(chars) for _ in range(8))

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password

def get_current_week_range():
    """Get the current week's Friday-Thursday range"""
    today = date.today()
    # Find the most recent Friday (or today if it's Friday)
    days_since_friday = (today.weekday() - 4) % 7  # Friday is 4
    week_start = today - timedelta(days=days_since_friday)
    week_end = week_start + timedelta(days=6)  # Thursday
    return week_start, week_end

def is_school_day():
    """Check if today is a school day (Monday-Friday)"""
    return date.today().weekday() < 5  # 0-4 is Mon-Fri

def auto_assign_daily_tasks(db: Session, family_id: int):
    """Auto-assign tasks based on day type"""
    today = date.today()
    is_weekday = today.weekday() < 5
    
    # Get all children in family
    children = db.query(User).filter(
        User.family_id == family_id,
        User.role == "child"
    ).all()
    
    # Get applicable tasks
    if is_weekday:
        tasks = db.query(Task).filter(
            Task.family_id == family_id,
            Task.day_type.in_(["weekday", "anyday"])
        ).all()
    else:
        tasks = db.query(Task).filter(
            Task.family_id == family_id,
            Task.day_type.in_(["weekend", "anyday"])
        ).all()
    
    # Assign tasks to children
    for child in children:
        for task in tasks:
            # Check if already assigned
            existing = db.query(TaskAssignment).filter(
                TaskAssignment.task_id == task.id,
                TaskAssignment.child_id == child.id
            ).first()
            
            if not existing:
                assignment = TaskAssignment(task_id=task.id, child_id=child.id)
                db.add(assignment)
    
    db.commit()

def update_weekly_progress(db: Session, child_id: int):
    """Update weekly progress for a child"""
    week_start, week_end = get_current_week_range()
    
    # Get or create weekly progress
    weekly = db.query(WeeklyProgress).filter(
        WeeklyProgress.child_id == child_id,
        WeeklyProgress.week_start == week_start
    ).first()
    
    if not weekly:
        weekly = WeeklyProgress(
            child_id=child_id,
            week_start=week_start,
            week_end=week_end
        )
        db.add(weekly)
    
    # Calculate total points for the week
    daily_records = db.query(DailyProgress).filter(
        DailyProgress.child_id == child_id,
        DailyProgress.date >= week_start,
        DailyProgress.date <= week_end
    ).all()
    
    weekly.total_points = sum(record.total_points for record in daily_records)
    weekly.tasks_completed = sum(
        len(json.loads(record.completed_task_ids)) for record in daily_records
    )
    
    db.commit()
    return weekly

def complete_task(db: Session, task_id: int, child_id: int, task_date: date = None):
    if task_date is None:
        task_date = date.today()
    
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        return False
    
    progress = db.query(DailyProgress).filter(
        DailyProgress.child_id == child_id,
        DailyProgress.date == task_date
    ).first()
    
    if not progress:
        progress = DailyProgress(child_id=child_id, date=task_date)
        db.add(progress)
    
    completed_ids = json.loads(progress.completed_task_ids)
    if task_id in completed_ids:
        return False
    
    completed_ids.append(task_id)
    progress.completed_task_ids = json.dumps(completed_ids)
    progress.total_points += task.points
    
    user = db.query(User).filter(User.id == child_id).first()
    user.total_lifetime_points += task.points
    
    db.commit()
    
    # Update weekly progress
    update_weekly_progress(db, child_id)
    
    return True

# Routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=303)
    
    if user.role in ["admin", "parent"]:
        return RedirectResponse("/parent/dashboard", status_code=303)
    else:
        return RedirectResponse("/child/dashboard", status_code=303)

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        return HTMLResponse('<div class="text-red-500">Invalid credentials</div>', status_code=400)
    
    token = create_session_token(user.id)
    response = RedirectResponse("/", status_code=303)
    response.set_cookie("session_token", token, httponly=True)
    return response

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
async def register(
    email: str = Form(...),
    password: str = Form(...),
    first_name: str = Form(...),
    last_name: str = Form(""),
    db: Session = Depends(get_db)
):
    if db.query(User).filter(User.email == email).first():
        return HTMLResponse('<div class="text-red-500">Email already registered</div>', status_code=400)
    
    user = User(
        email=email,
        password_hash=hash_password(password),
        first_name=first_name,
        last_name=last_name
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    token = create_session_token(user.id)
    response = RedirectResponse("/family-setup", status_code=303)
    response.set_cookie("session_token", token, httponly=True)
    return response

@app.get("/family-setup", response_class=HTMLResponse)
async def family_setup_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=303)
    if user.family_id:
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse("family_setup.html", {"request": request, "user": user})

@app.post("/create-family")
async def create_family(
    family_name: str = Form(...),
    request: Request = None,
    db: Session = Depends(get_db)
):
    user = get_current_user(request, db)
    if not user:
        raise HTTPException(status_code=401)
    
    join_code = generate_join_code()
    family = Family(name=family_name, join_code=join_code, admin_id=user.id)
    db.add(family)
    db.commit()
    db.refresh(family)
    
    user.family_id = family.id
    user.role = "admin"
    db.commit()
    
    return HTMLResponse(f'<div class="text-green-500">Family created! Join code: <strong>{join_code}</strong></div>')

@app.post("/join-family")
async def join_family(
    join_code: str = Form(...),
    request: Request = None,
    db: Session = Depends(get_db)
):
    user = get_current_user(request, db)
    if not user:
        raise HTTPException(status_code=401)
    
    family = db.query(Family).filter(Family.join_code == join_code.upper()).first()
    if not family:
        return HTMLResponse('<div class="text-red-500">Invalid join code</div>', status_code=400)
    
    user.family_id = family.id
    db.commit()
    
    return RedirectResponse("/", status_code=303)

@app.get("/child/dashboard", response_class=HTMLResponse)
async def child_dashboard(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user or not user.family_id:
        return RedirectResponse("/login", status_code=303)
    
    # Get today's progress
    today = date.today()
    progress = db.query(DailyProgress).filter(
        DailyProgress.child_id == user.id,
        DailyProgress.date == today
    ).first()
    
    if not progress:
        progress = DailyProgress(child_id=user.id, date=today)
        db.add(progress)
        db.commit()
    
    # Get weekly progress
    weekly = update_weekly_progress(db, user.id)
    week_start, week_end = get_current_week_range()
    
    # Check if auto-assignment is enabled
    family = db.query(Family).filter(Family.id == user.family_id).first()
    if family and family.auto_assign_enabled:
        auto_assign_daily_tasks(db, user.family_id)
    
    completed_ids = json.loads(progress.completed_task_ids)
    
    # Get assigned tasks
    assignments = db.query(TaskAssignment).filter(TaskAssignment.child_id == user.id).all()
    
    tasks_with_status = []
    for assignment in assignments:
        task = assignment.task
        # Filter by day type
        if task.day_type == "weekday" and not is_school_day():
            continue
        if task.day_type == "weekend" and is_school_day():
            continue
            
        tasks_with_status.append({
            "task": task,
            "completed": task.id in completed_ids
        })
    
    # Group by period
    morning_tasks = [t for t in tasks_with_status if t["task"].period == "morning"]
    evening_tasks = [t for t in tasks_with_status if t["task"].period == "evening"]
    anytime_tasks = [t for t in tasks_with_status if t["task"].period == "anytime"]
    
    return templates.TemplateResponse("child_dashboard.html", {
        "request": request,
        "user": user,
        "progress": progress,
        "weekly": weekly,
        "week_start": week_start,
        "week_end": week_end,
        "morning_tasks": morning_tasks,
        "evening_tasks": evening_tasks,
        "anytime_tasks": anytime_tasks
    })

@app.post("/complete-task/{task_id}")
async def complete_task_route(
    task_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    user = get_current_user(request, db)
    if not user:
        raise HTTPException(status_code=401)
    
    success = complete_task(db, task_id, user.id)
    if success:
        task = db.query(Task).filter(Task.id == task_id).first()
        return HTMLResponse(f'<div class="text-green-500">+{task.points} points! 🎉</div>')
    return HTMLResponse('<div class="text-yellow-500">Already completed</div>')

@app.get("/parent/dashboard", response_class=HTMLResponse)
async def parent_dashboard(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user or user.role not in ["admin", "parent"]:
        return RedirectResponse("/", status_code=303)
    
    # Get family children
    children = db.query(User).filter(
        User.family_id == user.family_id,
        User.role == "child"
    ).all()
    
    # Get today's progress for each child
    today = date.today()
    week_start, week_end = get_current_week_range()
    
    children_progress = []
    for child in children:
        progress = db.query(DailyProgress).filter(
            DailyProgress.child_id == child.id,
            DailyProgress.date == today
        ).first()
        
        weekly = db.query(WeeklyProgress).filter(
            WeeklyProgress.child_id == child.id,
            WeeklyProgress.week_start == week_start
        ).first()
        
        completed_count = len(json.loads(progress.completed_task_ids)) if progress else 0
        children_progress.append({
            "child": child,
            "points": progress.total_points if progress else 0,
            "completed_count": completed_count,
            "weekly_points": weekly.total_points if weekly else 0
        })
    
    family = db.query(Family).filter(Family.id == user.family_id).first()
    
    return templates.TemplateResponse("parent_dashboard.html", {
        "request": request,
        "user": user,
        "family": family,
        "children_progress": children_progress,
        "week_start": week_start,
        "week_end": week_end
    })

@app.get("/parent/manage-tasks", response_class=HTMLResponse)
async def manage_tasks(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user or user.role not in ["admin", "parent"]:
        return RedirectResponse("/", status_code=303)
    
    # Get all tasks for this family
    tasks = db.query(Task).filter(Task.family_id == user.family_id).all()
    
    # Get all children in family for assignment
    children = db.query(User).filter(
        User.family_id == user.family_id,
        User.role == "child"
    ).all()
    
    return templates.TemplateResponse("manage_tasks.html", {
        "request": request,
        "user": user,
        "tasks": tasks,
        "children": children
    })

@app.post("/parent/create-task")
async def create_task(
    title: str = Form(...),
    points: int = Form(...),
    icon: str = Form("⭐"),
    period: str = Form("anytime"),
    category: str = Form("daily"),
    day_type: str = Form("anyday"),
    request: Request = None,
    db: Session = Depends(get_db)
):
    user = get_current_user(request, db)
    if not user or user.role not in ["admin", "parent"]:
        raise HTTPException(status_code=401)
    
    # Create task
    task = Task(
        family_id=user.family_id,
        title=title,
        points=points,
        icon=icon,
        period=period,
        category=category,
        day_type=day_type
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    
    # Auto-assign to all children in family
    children = db.query(User).filter(
        User.family_id == user.family_id,
        User.role == "child"
    ).all()
    
    for child in children:
        assignment = TaskAssignment(task_id=task.id, child_id=child.id)
        db.add(assignment)
    
    db.commit()
    
    return HTMLResponse(f'<div class="text-green-500">Task created and assigned to {len(children)} child(ren)! ✅</div>')

@app.post("/parent/delete-task/{task_id}")
async def delete_task(
    task_id: int,
    request: Request = None,
    db: Session = Depends(get_db)
):
    user = get_current_user(request, db)
    if not user or user.role not in ["admin", "parent"]:
        raise HTTPException(status_code=401)
    
    task = db.query(Task).filter(Task.id == task_id).first()
    if task and task.family_id == user.family_id:
        db.delete(task)
        db.commit()
        return HTMLResponse('<div class="text-green-500">Task deleted! 🗑️</div>')
    
    return HTMLResponse('<div class="text-red-500">Task not found</div>', status_code=404)

@app.get("/parent/settings", response_class=HTMLResponse)
async def family_settings(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user or user.role not in ["admin", "parent"]:
        return RedirectResponse("/", status_code=303)
    
    family = db.query(Family).filter(Family.id == user.family_id).first()
    
    return templates.TemplateResponse("family_settings.html", {
        "request": request,
        "user": user,
        "family": family
    })

@app.post("/parent/update-settings")
async def update_settings(
    auto_assign_enabled: bool = Form(False),
    request: Request = None,
    db: Session = Depends(get_db)
):
    user = get_current_user(request, db)
    if not user or user.role not in ["admin", "parent"]:
        raise HTTPException(status_code=401)
    
    family = db.query(Family).filter(Family.id == user.family_id).first()
    family.auto_assign_enabled = auto_assign_enabled
    db.commit()
    
    return HTMLResponse('<div class="text-green-500">✅ Settings saved!</div>')

@app.get("/logout")
async def logout():
    response = RedirectResponse("/login", status_code=303)
    response.delete_cookie("session_token")
    return response

@app.get("/parent/manage-rewards", response_class=HTMLResponse)
async def manage_rewards(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user or user.role not in ["admin", "parent"]:
        return RedirectResponse("/", status_code=303)
    
    rewards = db.query(Reward).filter(Reward.family_id == user.family_id).all()
    
    return templates.TemplateResponse("manage_rewards.html", {
        "request": request,
        "user": user,
        "rewards": rewards
    })

@app.post("/parent/create-reward")
async def create_reward(
    name: str = Form(...),
    cost: int = Form(...),
    icon: str = Form("🎁"),
    reward_type: str = Form("special"),
    description: str = Form(""),
    request: Request = None,
    db: Session = Depends(get_db)
):
    user = get_current_user(request, db)
    if not user or user.role not in ["admin", "parent"]:
        raise HTTPException(status_code=401)
    
    reward = Reward(
        family_id=user.family_id,
        name=name,
        cost=cost,
        icon=icon,
        reward_type=reward_type,
        description=description
    )
    db.add(reward)
    db.commit()
    
    return HTMLResponse('<div class="text-green-500">Reward created! ✅</div>')

@app.post("/parent/delete-reward/{reward_id}")
async def delete_reward(
    reward_id: int,
    request: Request = None,
    db: Session = Depends(get_db)
):
    user = get_current_user(request, db)
    if not user or user.role not in ["admin", "parent"]:
        raise HTTPException(status_code=401)
    
    reward = db.query(Reward).filter(Reward.id == reward_id).first()
    if reward and reward.family_id == user.family_id:
        db.delete(reward)
        db.commit()
        return HTMLResponse('<div class="text-green-500">Reward deleted! 🗑️</div>')
    
    return HTMLResponse('<div class="text-red-500">Reward not found</div>', status_code=404)

@app.get("/child/rewards", response_class=HTMLResponse)
async def child_rewards(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user or not user.family_id:
        return RedirectResponse("/login", status_code=303)
    
    # Get weekly progress
    weekly = update_weekly_progress(db, user.id)
    week_start, week_end = get_current_week_range()
    
    # Check if today is Friday (unlock day)
    today = date.today()
    is_friday = today.weekday() == 4
    
    # Get all rewards
    rewards = db.query(Reward).filter(Reward.family_id == user.family_id).all()
    
    return templates.TemplateResponse("child_rewards.html", {
        "request": request,
        "user": user,
        "rewards": rewards,
        "weekly": weekly,
        "week_start": week_start,
        "week_end": week_end,
        "is_friday": is_friday
    })

@app.post("/child/redeem-reward/{reward_id}")
async def redeem_reward(
    reward_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    user = get_current_user(request, db)
    if not user:
        raise HTTPException(status_code=401)
    
    # Check if it's Friday
    today = date.today()
    if today.weekday() != 4:
        return HTMLResponse('<div class="text-red-500">❌ Rewards only unlock on Fridays!</div>', status_code=400)
    
    reward = db.query(Reward).filter(Reward.id == reward_id).first()
    if not reward:
        return HTMLResponse('<div class="text-red-500">Reward not found</div>', status_code=404)
    
    # Get weekly progress
    weekly = update_weekly_progress(db, user.id)
    
    if weekly.total_points < reward.cost:
        return HTMLResponse(f'<div class="text-red-500">❌ Not enough points! Need {reward.cost - weekly.total_points} more.</div>', status_code=400)
    
    # Deduct points from weekly total
    weekly.total_points -= reward.cost
    db.commit()
    
    return HTMLResponse(f'<div class="text-green-500">🎉 {reward.name} redeemed! Enjoy!</div>')

@app.get("/parent/calendar", response_class=HTMLResponse)
async def parent_calendar(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user or user.role not in ["admin", "parent"]:
        return RedirectResponse("/", status_code=303)
    
    # Get all calendar events for this family
    events = db.query(CalendarEvent).filter(
        CalendarEvent.family_id == user.family_id
    ).order_by(CalendarEvent.event_date).all()
    
    return templates.TemplateResponse("parent_calendar.html", {
        "request": request,
        "user": user,
        "events": events
    })

@app.post("/parent/create-event")
async def create_event(
    title: str = Form(...),
    description: str = Form(""),
    event_date: str = Form(...),
    event_time: str = Form(""),
    event_type: str = Form("activity"),
    points_for_completion: int = Form(15),
    request: Request = None,
    db: Session = Depends(get_db)
):
    user = get_current_user(request, db)
    if not user or user.role not in ["admin", "parent"]:
        raise HTTPException(status_code=401)
    
    from datetime import datetime as dt
    
    event = CalendarEvent(
        family_id=user.family_id,
        title=title,
        description=description,
        event_date=dt.strptime(event_date, "%Y-%m-%d").date(),
        event_time=event_time if event_time else None,
        event_type=event_type,
        points_for_completion=points_for_completion,
        created_by=user.id
    )
    db.add(event)
    db.commit()
    
    return HTMLResponse('<div class="text-green-500">Event created! ✅</div>')

@app.post("/parent/delete-event/{event_id}")
async def delete_event(
    event_id: int,
    request: Request = None,
    db: Session = Depends(get_db)
):
    user = get_current_user(request, db)
    if not user or user.role not in ["admin", "parent"]:
        raise HTTPException(status_code=401)
    
    event = db.query(CalendarEvent).filter(CalendarEvent.id == event_id).first()
    if event and event.family_id == user.family_id:
        db.delete(event)
        db.commit()
        return HTMLResponse('<div class="text-green-500">Event deleted! 🗑️</div>')
    
    return HTMLResponse('<div class="text-red-500">Event not found</div>', status_code=404)

@app.post("/parent/complete-event/{event_id}")
async def complete_event(
    event_id: int,
    request: Request = None,
    db: Session = Depends(get_db)
):
    user = get_current_user(request, db)
    if not user or user.role not in ["admin", "parent"]:
        raise HTTPException(status_code=401)
    
    event = db.query(CalendarEvent).filter(CalendarEvent.id == event_id).first()
    if not event or event.family_id != user.family_id:
        return HTMLResponse('<div class="text-red-500">Event not found</div>', status_code=404)
    
    event.is_completed = True
    db.commit()
    
    return HTMLResponse(f'<div class="text-green-500">✅ Event completed! Awarded {event.points_for_completion} points</div>')

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)