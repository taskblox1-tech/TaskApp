import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.family import Family
from app.models.profile import Profile, UserRole
from app.models.task import Task, TaskPeriod, TaskCategory, TaskDayType
from app.models.task_assignment import TaskAssignment
from app.models.reward import Reward, RewardType
import hashlib
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def generate_join_code():
    import random, string
    chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
    return ''.join(random.choice(chars) for _ in range(8))

# All 58 tasks organized by category
TASK_LIBRARY = {
    "daily_routine": [
        {"title": "Doors Closed and Locked", "points": 45, "icon": "🔒", "period": "evening", "category": "daily", "day_type": "anyday"},
        {"title": "Key Put Away", "points": 25, "icon": "🔑", "period": "evening", "category": "daily", "day_type": "anyday"},
        {"title": "Shoes Put Away", "points": 30, "icon": "👟", "period": "evening", "category": "daily", "day_type": "anyday"},
        {"title": "Room Clean", "points": 60, "icon": "🧹", "period": "evening", "category": "daily", "day_type": "anyday"},
        {"title": "Reading 15 Minutes", "points": 70, "icon": "📚", "period": "evening", "category": "daily", "day_type": "anyday"},
        {"title": "Laundry in Basement", "points": 40, "icon": "👔", "period": "evening", "category": "daily", "day_type": "anyday"},
        {"title": "Gate Closed", "points": 35, "icon": "🚪", "period": "evening", "category": "daily", "day_type": "anyday"},
        {"title": "Backpack Organized", "points": 30, "icon": "🎒", "period": "morning", "category": "daily", "day_type": "weekday"},
        {"title": "Socks and Shoes", "points": 20, "icon": "🧦", "period": "morning", "category": "daily", "day_type": "weekday"},
        {"title": "Filling Water Bottle", "points": 30, "icon": "💧", "period": "morning", "category": "daily", "day_type": "weekday"},
        {"title": "Eat Breakfast", "points": 50, "icon": "🍳", "period": "morning", "category": "daily", "day_type": "anyday"},
        {"title": "Brush Teeth", "points": 40, "icon": "🪥", "period": "morning", "category": "daily", "day_type": "anyday"},
        {"title": "Get Dressed", "points": 25, "icon": "👕", "period": "morning", "category": "daily", "day_type": "anyday"},
        {"title": "Take Medicine", "points": 60, "icon": "💊", "period": "morning", "category": "daily", "day_type": "anyday"},
        {"title": "Homework Completed", "points": 80, "icon": "📚", "period": "evening", "category": "daily", "day_type": "weekday"},
        {"title": "Family Time", "points": 80, "icon": "👨‍👩‍👧", "period": "evening", "category": "bonus", "day_type": "weekend"},
        {"title": "Reading 30 Minutes", "points": 100, "icon": "📖", "period": "evening", "category": "bonus", "day_type": "weekend"},
        {"title": "Prepare for Week", "points": 50, "icon": "📅", "period": "evening", "category": "general", "day_type": "weekend"},
        {"title": "Help with Chores", "points": 70, "icon": "🏠", "period": "anytime", "category": "bonus", "day_type": "anyday"},
    ]
}

SAMPLE_REWARDS = [
    {"name": "30 Min Screen Time", "cost": 50, "icon": "📺", "type": "screen_time"},
    {"name": "Video Game Hour", "cost": 100, "icon": "🎮", "type": "screen_time"},
    {"name": "Ice Cream Trip", "cost": 80, "icon": "🍦", "type": "treat"},
    {"name": "Movie Night", "cost": 200, "icon": "🎬", "type": "activity"},
    {"name": "Extra $5", "cost": 150, "icon": "💵", "type": "allowance"},
    {"name": "Stay Up Late", "cost": 120, "icon": "🌙", "type": "privilege"},
]

def main():
    db = SessionLocal()
    
    try:
        # Check existing
        if db.query(Family).first():
            logger.warning("⚠️  Data already exists!")
            response = input("Clear and reseed? (yes/no): ")
            if response.lower() != "yes":
                return
            
            db.query(TaskAssignment).delete()
            db.query(Task).delete()
            db.query(Reward).delete()
            db.query(Profile).delete()
            db.query(Family).delete()
            db.commit()
        
        logger.info("="*60)
        logger.info("CREATING LEFEBVRE FAMILY")
        logger.info("="*60)
        
        # Create family
        family = Family(name="Lefebvre Family", join_code=generate_join_code())
        db.add(family)
        db.flush()
        
        # Create admin
        admin = Profile(
            family_id=family.id,
            email="armand@lefebvre.com",
            password_hash=hash_password("password"),
            first_name="Armand",
            last_name="Lefebvre",
            role=UserRole.ADMIN,
            theme="sports"
        )
        db.add(admin)
        db.flush()
        family.admin_id = admin.id
        
        # Create children
        little_armand = Profile(
            family_id=family.id,
            email="little.armand@lefebvre.com",
            password_hash=hash_password("password"),
            first_name="Little Armand",
            last_name="Lefebvre",
            role=UserRole.CHILD,
            theme="minecraft"
        )
        giuliana = Profile(
            family_id=family.id,
            email="giuliana@lefebvre.com",
            password_hash=hash_password("password"),
            first_name="Giuliana",
            last_name="Lefebvre",
            role=UserRole.CHILD,
            theme="barbie"
        )
        db.add_all([little_armand, giuliana])
        db.flush()
        
        logger.info(f"✅ Family: {family.name} (Code: {family.join_code})")
        logger.info(f"✅ Admin: {admin.first_name}")
        logger.info(f"✅ Child: {little_armand.first_name} - {little_armand.theme}")
        logger.info(f"✅ Child: {giuliana.first_name} - {giuliana.theme}")
        
        # Add tasks
        logger.info("\n"+"="*60)
        logger.info("ADDING TASKS")
        logger.info("="*60)
        
        children = [little_armand, giuliana]
        task_count = 0
        
        for cat, tasks in TASK_LIBRARY.items():
            for td in tasks:
                task = Task(
                    family_id=family.id,
                    title=td["title"],
                    points=td["points"],
                    icon=td["icon"],
                    period=TaskPeriod[td["period"].upper()],
                    category=TaskCategory[td["category"].upper()],
                    day_type=TaskDayType[td["day_type"].upper()],
                    library_category=cat
                )
                db.add(task)
                db.flush()
                task_count += 1
                
                for child in children:
                    db.add(TaskAssignment(task_id=task.id, child_id=child.id))
                
                logger.info(f"  ✓ {td['icon']} {td['title']} - {td['points']}pts")
        
        # Add rewards
        for rd in SAMPLE_REWARDS:
            reward = Reward(
                family_id=family.id,
                name=rd["name"],
                cost=rd["cost"],
                icon=rd["icon"],
                type=RewardType[rd["type"].upper()]
            )
            db.add(reward)
        
        db.commit()
        
        logger.info("\n"+"="*60)
        logger.info("✅ COMPLETE!")
        logger.info("="*60)
        logger.info(f"\n📊 Created:")
        logger.info(f"   {task_count} tasks")
        logger.info(f"   {len(SAMPLE_REWARDS)} rewards")
        logger.info(f"\n🔑 Logins:")
        logger.info(f"   armand@lefebvre.com / password")
        logger.info(f"   little.armand@lefebvre.com / password")
        logger.info(f"   giuliana@lefebvre.com / password")
        logger.info(f"\n🚀 Start: uvicorn app.main:app --reload")
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()