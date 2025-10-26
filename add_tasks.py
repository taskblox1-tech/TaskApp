"""
Quick script to add all tasks with day_type to the database
Run this once: python add_tasks.py
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import Task, User, Family, TaskAssignment, Base

# Connect to database
engine = create_engine("sqlite:///./family_tasks.db")
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

# Create a test family and users first
print("Creating test family and users...")

# Create family
family = Family(name="Lefebvre Family", join_code="TEST1234", admin_id=1)
db.add(family)
db.commit()
db.refresh(family)

# Create admin/parent
from main import hash_password
admin = User(
    email="armand@test.com",
    password_hash=hash_password("password"),
    first_name="Armand",
    last_name="Lefebvre",
    family_id=family.id,
    role="admin"
)
db.add(admin)
db.commit()

# Update family admin_id
family.admin_id = admin.id
db.commit()

# Create children
child1 = User(
    email="little.armand@test.com",
    password_hash=hash_password("password"),
    first_name="Little Armand",
    last_name="Lefebvre",
    family_id=family.id,
    role="child"
)
db.add(child1)

child2 = User(
    email="giuliana@test.com",
    password_hash=hash_password("password"),
    first_name="Giuliana",
    last_name="Lefebvre",
    family_id=family.id,
    role="child"
)
db.add(child2)

db.commit()
print(f"✓ Created family: {family.name} (Join Code: {family.join_code})")
print(f"✓ Created admin: {admin.first_name} ({admin.email})")
print(f"✓ Created children: {child1.first_name}, {child2.first_name}")

FAMILY_ID = family.id

tasks_to_add = [
    # Evening tasks - Anyday
    {"title": "Doors Closed and Locked", "points": 45, "icon": "🔒", "period": "evening", "category": "daily", "day_type": "anyday"},
    {"title": "Key Put Away", "points": 25, "icon": "🔑", "period": "evening", "category": "daily", "day_type": "anyday"},
    {"title": "Shoes Put Away", "points": 30, "icon": "👟", "period": "evening", "category": "daily", "day_type": "anyday"},
    {"title": "Room Clean", "points": 60, "icon": "🧹", "period": "evening", "category": "daily", "day_type": "anyday"},
    {"title": "Reading 15 Minutes", "points": 70, "icon": "📚", "period": "evening", "category": "daily", "day_type": "anyday"},
    {"title": "Laundry in Basement", "points": 40, "icon": "👔", "period": "evening", "category": "daily", "day_type": "anyday"},
    {"title": "Gate Closed", "points": 35, "icon": "🚪", "period": "evening", "category": "daily", "day_type": "anyday"},
    
    # Morning tasks - Weekday (school days)
    {"title": "Backpack Organized", "points": 30, "icon": "🎒", "period": "morning", "category": "daily", "day_type": "weekday"},
    {"title": "Socks and Shoes", "points": 20, "icon": "🧦", "period": "morning", "category": "daily", "day_type": "weekday"},
    {"title": "Filling Water Bottle for school", "points": 30, "icon": "💧", "period": "morning", "category": "daily", "day_type": "weekday"},
    
    # Morning tasks - Anyday
    {"title": "Eat Breakfast", "points": 50, "icon": "🍳", "period": "morning", "category": "daily", "day_type": "anyday"},
    {"title": "Brush Teeth", "points": 40, "icon": "🪥", "period": "morning", "category": "daily", "day_type": "anyday"},
    {"title": "Get Dressed", "points": 25, "icon": "👕", "period": "morning", "category": "daily", "day_type": "anyday"},
    {"title": "Take Medicine", "points": 60, "icon": "💊", "period": "morning", "category": "daily", "day_type": "anyday"},
    
    # Evening tasks - Weekday
    {"title": "Homework Completed", "points": 80, "icon": "📚", "period": "evening", "category": "daily", "day_type": "weekday"},
    
    # Evening tasks - Weekend
    {"title": "Family Time Activity", "points": 80, "icon": "👨‍👩‍👧", "period": "evening", "category": "bonus", "day_type": "weekend"},
    {"title": "Reading 30 Minutes", "points": 100, "icon": "📖", "period": "evening", "category": "bonus", "day_type": "weekend"},
    {"title": "Prepare for Next Week", "points": 50, "icon": "📅", "period": "evening", "category": "general", "day_type": "weekend"},
    
    # Anytime tasks
    {"title": "Help with Chores", "points": 70, "icon": "🏠", "period": "anytime", "category": "bonus", "day_type": "anyday"},
]

print("\nAdding tasks to database...")

for task_data in tasks_to_add:
    task = Task(
        family_id=FAMILY_ID,
        **task_data
    )
    db.add(task)
    print(f"✓ Added: {task_data['title']} ({task_data['day_type']})")

db.commit()
print(f"\n🎉 Successfully added {len(tasks_to_add)} tasks!")

# Now auto-assign to all children
children = db.query(User).filter(User.family_id == FAMILY_ID, User.role == "child").all()
all_tasks = db.query(Task).filter(Task.family_id == FAMILY_ID).all()

print(f"\nAssigning {len(all_tasks)} tasks to {len(children)} children...")

for child in children:
    for task in all_tasks:
        assignment = TaskAssignment(task_id=task.id, child_id=child.id)
        db.add(assignment)

db.commit()
print(f"✓ All tasks assigned to all children!")
print("\n" + "="*50)
print("✅ SETUP COMPLETE!")
print("="*50)
print(f"\n📧 Login credentials:")
print(f"   Admin: armand@test.com / password")
print(f"   Child 1: little.armand@test.com / password")
print(f"   Child 2: giuliana@test.com / password")
print(f"\n🔑 Family Join Code: {family.join_code}")
print("\n🚀 Start the app: python main.py")
print("   Then go to: http://localhost:8000\n")

db.close()