# Family Task Tracker

A comprehensive gamified task management system for families with 60+ pre-loaded task templates, approval workflows, points, and rewards. Perfect for teaching responsibility, building good habits, and motivating children with achievements and rewards.

## ✨ Latest Updates

### 🎨 Theme System with Animations & Streaks (New!)
**Gamified Experience for Kids:**
- **5 Engaging Themes**: Minecraft, Roblox, Barbie, Pokémon, Ninja Turtles
- **Custom Theme Elements**:
  - Unique color schemes and backgrounds
  - Theme-specific icons for points, tasks, and rewards
  - Character avatars to choose from
  - Sound effects for task completion (ready for audio files)
- **Animated Celebrations**:
  - Flying points animation - points fly from task to counter
  - Confetti burst on task completion
  - Screen shake for high-value tasks (100+ points)
  - Toast notifications with theme styling
  - Counter increment animations
- **Streak System**:
  - Track consecutive days of task completion
  - Animated streak badge with pulsing fire icon
  - Longest streak record keeping
  - Milestone celebrations (3, 7, 14, 30, 60, 100 days)
  - Automatic reset if a day is missed
- **Theme Selector**: Kids choose their favorite theme and avatar during registration

### 📊 Enhanced Parent Dashboard (New!)
**Comprehensive Family Insights:**
- **Live Date/Time Display** - Real-time clock in dashboard header, updates every minute
- **Personalized Welcome** - Shows current user's name in header
- **Enhanced Children Stats** - Detailed cards for each child showing:
  - Today's points earned and tasks completed
  - Pending approvals count
  - Total rewards claimed
  - Visual completion progress bar
  - Total lifetime points with star badge
  - Last activity timestamp (e.g., "2 hours ago", "Yesterday")
- **Family Members Tab** - New dedicated section showing:
  - All family members (parents and children)
  - Email addresses and roles
  - Last login times with smart formatting
  - "Just now", "5 mins ago", "2 hours ago" for recent activity
  - Highlighted "(You)" badge for current user
  - Points display for children

### 🔧 Bulk Task Management (New!)
**Efficient Multi-Task Operations:**
- **Selection Mode** - Click "Select" button to enable checkbox mode
- **Select All** - Quickly select all tasks at once
- **Bulk Assign** - Assign multiple tasks to children simultaneously
- **Bulk Delete** - Delete multiple tasks with one action
- **Visual Feedback** - Selected tasks highlighted with blue border
- **Progress Tracking** - Shows count of selected tasks during operations

### 📋 Enhanced Task Display (New!)
**Better Task Visibility:**
- **Assigned Children Display** - Each task card shows who it's assigned to
- **Quick Task Actions** - Assign, Edit, Delete buttons on each task
- **Task Assignment Modal** - Dedicated interface for assigning tasks to children
- **Assignment Tracking** - See task assignments at a glance without opening edit mode

### 🎯 Task Template Library
**60+ Pre-loaded Tasks Across 9 Categories**
- No more creating tasks from scratch
- 3-step wizard: Choose category → Select template → Customize
- Customize any template (title, points, icon, schedule, approval settings)
- Or create completely custom tasks

**Categories Include:**
1. **Morning Tasks** (Weekday/Weekend/Anyday) - Breakfast, teeth brushing, backpack prep
2. **Evening Tasks** (Weekday/Weekend/Anyday) - Homework, room clean, bedtime routine
3. **Academic Excellence** - Perfect test scores, teacher praise, grade improvements
4. **Health & Fitness** - Exercise, water intake, outdoor play
5. **Character & Behavior** - Kindness, respect, good attitude
6. **Extra Household Tasks** - Cooking help, cleaning, organizing
7. **Creative & Development** - Music practice, art, journaling
8. **Bonus Challenges** - Screen-free days, reading goals, weekly achievements

**Smart Point System:**
- Daily basics: 20-60 points
- Extra effort tasks: 65-90 points
- Academic achievements: 100-150 points
- Major accomplishments: 150-200 points

### 🔐 Parent Approval System
- Toggle "requires approval" on any task
- Perfect for academic achievements, behavior rewards, and teacher feedback
- Children see "Pending Approval" badge on submitted tasks
- Parents review and approve/deny from their dashboard
- Points awarded only after parent approval

### 👨‍👩‍👧 Family Management
- Easy registration with family join codes
- Parents create families automatically
- Children join with 6-character family code
- Multiple children per family supported
- Theme customization for each child

## ✅ Core Features

### Authentication & Authorization
- JWT token-based authentication
- Role-based access (Parent and Child)
- Secure password hashing with bcrypt
- Cookie-based sessions (7-day expiry)
- Family join code system

### Task Management
- **60+ pre-loaded task templates** organized by category
- Create custom tasks or use templates
- Assign tasks to specific children or all children
- Task scheduling (Morning/Evening/Anytime)
- Day type filtering (Weekday/Weekend/Anyday)
- Customizable icons, points, and descriptions
- Parent approval toggle for sensitive tasks

### Approval System
- Tasks can require parent approval before awarding points
- Children submit completed tasks with "nudge" button
- Parents see pending approvals in dedicated tab
- Approve or deny with one click
- Perfect for academic achievements and character development

### Rewards
- Define rewards with point costs
- Children can see what they're working toward
- Track lifetime points across all tasks
- Visual indicators showing affordable rewards

### Dashboards

**Parent Dashboard:**
- **Header**: Live date/time display, personalized welcome message with user name
- **Family Stats**: Real-time stats (total children, tasks, approvals, family points)
- **5 Organized Tabs**:
  - **Children Tab**: Enhanced cards with today's progress, completion rates, pending approvals, rewards claimed, last activity
  - **Family Members Tab**: All family members with email, role, last login times, points (for children)
  - **Approvals Tab**: Review and approve/deny pending task completions
  - **All Tasks Tab**: Complete task management with bulk operations (select, assign, delete)
  - **Rewards Tab**: Create, edit, and delete rewards
- **Task Management**:
  - 3-step task creation wizard with 60+ templates
  - Bulk operations: Select multiple tasks to assign or delete
  - Quick actions: Assign, Edit, Delete buttons on each task
  - Shows assigned children directly on task cards
- **Quick Actions Panel**: Fast access to common tasks
- **Family Join Code**: Easy copy button to share with family members

**Child Dashboard:**
- Personalized greeting with chosen theme icon
- Large points display showing total achievements
- Today's progress tracking with visual progress bar
- Task filters (All, Morning, Evening, Anytime)
- One-tap task completion
- "Pending Approval" badges for tasks awaiting parent review
- Rewards preview showing what's achievable

## 🚀 Quick Start

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Start the server
python main.py

# Access at http://localhost:8000
```

### Deploy to Render.com

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin YOUR_GITHUB_REPO_URL
   git push -u origin main
   ```

2. **Create Render Blueprint**
   - Go to https://dashboard.render.com
   - New + → Blueprint
   - Connect your GitHub repo
   - Render auto-detects `render.yaml`
   - Click "Apply"

3. **Initialize Database** (in Render Shell)
   ```bash
   python -c "from app.database import Base, engine; Base.metadata.create_all(bind=engine)"
   ```

4. **Create Admin User** (in Render Shell)
   ```python
   from app.database import SessionLocal
   from app.models.family import Family
   from app.models.profile import Profile, UserRole
   from app.core.security import get_password_hash

   db = SessionLocal()
   family = Family(name='Your Family')
   db.add(family)
   db.commit()

   parent = Profile(
       family_id=family.id,
       email='your@email.com',
       password_hash=get_password_hash('your-password'),
       first_name='First',
       last_name='Last',
       role=UserRole.ADMIN
   )
   db.add(parent)
   db.commit()
   ```

## 📁 Project Structure

```
family-task-tracker/
├── app/
│   ├── api/                    # API endpoints
│   │   ├── auth.py            # Registration, login, theme updates, user management, children stats
│   │   ├── tasks.py           # Task CRUD, completion with streak tracking, templates, assignments, bulk operations
│   │   ├── approvals.py       # Task approval workflow
│   │   ├── rewards.py         # Reward CRUD operations
│   │   └── families.py        # Family join codes, family members list with last login
│   ├── core/                   # Security, dependencies
│   ├── models/                 # Database models
│   │   ├── task.py            # Task model with approval field
│   │   ├── profile.py         # User/child profiles with theme, avatar, streaks
│   │   ├── family.py          # Family with join codes
│   │   ├── daily_progress.py  # Daily completion tracking
│   │   └── task_approval.py   # Approval requests
│   ├── config.py               # Environment settings
│   ├── database.py             # PostgreSQL connection
│   └── main.py                 # FastAPI app
├── static/
│   ├── css/
│   │   └── main.css           # Custom styles with theme animations
│   └── js/
│       ├── app.js             # General app JavaScript
│       ├── themes.js          # Theme configurations (5 themes)
│       ├── animations.js      # Animation system (confetti, flying points, etc.)
│       └── task-templates.js  # 60+ pre-loaded task templates
├── templates/                  # Jinja2 templates
│   ├── child/
│   │   └── dashboard.html     # Child task view with approval badges
│   ├── parent/
│   │   └── dashboard.html     # Parent view with 3-step task wizard
│   ├── auth/
│   │   ├── login.html
│   │   └── register.html      # Family creation/joining
│   └── base.html              # Base template
├── requirements.txt            # Python dependencies
├── render.yaml                 # Render.com deployment config
└── README.md                   # This file
```

## 🔑 Environment Variables

Set these in Render.com:
- `DATABASE_URL`: Auto-set by Render PostgreSQL
- `SECRET_KEY`: Auto-generated by Render
- `ENVIRONMENT`: Set to "production"

## 🎯 Usage Flow

### Getting Started
1. **Parent** creates account (auto-generates family join code)
2. **Parent** shares join code with children
3. **Children** register using join code and choose theme

### Creating Tasks (3-Step Wizard)
1. **Choose Category** - Select from 9 pre-loaded categories or create custom
2. **Select Template** - Pick from category templates or skip to custom
3. **Customize** - Adjust title, points, icon, schedule, approval settings, and assign to children

### Daily Usage
1. **Child** logs in and sees assigned tasks organized by time (Morning/Evening/Anytime)
2. **Child** completes tasks by tapping the icon
   - Tasks without approval: Instant points awarded
   - Tasks with approval: Marked "Pending Approval"
3. **Parent** reviews pending approvals in Approvals tab
4. **Parent** approves or denies with one click
5. **Child** earns points and can view available rewards

### Example Task Workflows

**Academic Achievement:**
- Parent creates "Perfect Test Score" task (requires approval, 150 pts)
- Child completes test and marks task as done
- Child shows test to parent
- Parent approves task → Child earns 150 points

**Daily Routine:**
- Parent creates "Brush Teeth" task (no approval, 40 pts)
- Child brushes teeth and marks complete
- Points awarded immediately
- Task resets daily

## 📚 Tech Stack

- **Backend**: FastAPI + SQLAlchemy
- **Database**: PostgreSQL
- **Frontend**: Alpine.js + Tailwind CSS
- **Auth**: JWT tokens
- **Hosting**: Render.com

## 🐛 Troubleshooting

### Login Issues
- Clear cookies and try again
- Check that SECRET_KEY is set in environment

### Database Connection
- Verify DATABASE_URL environment variable
- Check Render database status

### Tasks Not Loading
- Check browser console for errors
- Verify user has family_id set
- Check that tasks are assigned to child

## 📝 License

MIT License - feel free to use for your family!
