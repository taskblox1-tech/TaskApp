# Testing Checklist for Family Task Tracker

## Server Status
✅ Server is running on http://localhost:8000

## Pre-Test Setup
Current database has:
- ✅ 1 family (Lefebvre Family)
- ✅ 1 admin user (armand@lefebvre.com)
- ✅ 2 children (little.armand@lefebvre.com, giuliana@lefebvre.com)
- ✅ 19 tasks
- ✅ 38 task assignments
- ✅ 6 rewards
- ✅ 5 tasks set to require approval

## Test Plan

### 1. Authentication Tests

#### Test 1.1: Login as Admin
1. Go to http://localhost:8000
2. Login as: armand@lefebvre.com / (your password)
3. Should redirect to /parent/dashboard
4. ✅ PASS if you see the parent dashboard

#### Test 1.2: Login as Child
1. Logout
2. Login as: little.armand@lefebvre.com / (your password)
3. Should redirect to /dashboard (child view)
4. ✅ PASS if you see child dashboard with tasks

### 2. Child Dashboard Tests

#### Test 2.1: View Tasks
While logged in as child:
1. Check that tasks are displayed
2. Verify tasks are grouped by period (Morning/Evening/Anytime)
3. ✅ PASS if tasks show with icons and point values

#### Test 2.2: Complete a Regular Task (No Approval)
1. Find a task that does NOT have the 🔔 icon
2. Click the circle/checkbox to complete it
3. Should see success alert: "Task completed! You earned X points!"
4. Task should turn green with checkmark
5. ✅ PASS if points are added to your total

#### Test 2.3: Complete a Task Requiring Approval
1. Find a task WITH the 🔔 icon (one of these):
   - Doors Closed and Locked
   - Key Put Away
   - Shoes Put Away
   - Room Clean
   - Reading 15 Minutes
2. Click to complete it
3. Should see alert: "Task submitted for approval!"
4. Task should show "Pending Approval" badge
5. ✅ PASS if no points added yet (awaiting approval)

### 3. Parent Dashboard Tests

#### Test 3.1: View Pending Approvals
1. Logout from child account
2. Login as admin (armand@lefebvre.com)
3. Go to parent dashboard
4. Click on "Approvals" tab
5. Should see the approval request you just created
6. ✅ PASS if approval shows:
   - Task name
   - Child name
   - Approve/Deny buttons

#### Test 3.2: Approve a Task
1. Click "Approve" button on a pending approval
2. Confirm when prompted
3. Should see "Task approved!" message
4. Approval should disappear from list
5. Check "Pending Approvals" counter - should decrease
6. ✅ PASS if approval is processed

#### Test 3.3: Deny a Task
1. Have child complete another approval task
2. As parent, click "Deny" on the approval
3. Confirm when prompted
4. Should see "Task denied" message
5. Approval should disappear
6. ✅ PASS if no points awarded to child

### 4. Points System Tests

#### Test 4.1: Verify Points Tracking
1. Login as child
2. Note your current total points
3. Complete a regular task (no approval)
4. Verify points increased by task's point value
5. ✅ PASS if points update correctly

#### Test 4.2: Verify Approval Points
1. Complete a task requiring approval
2. Note points did NOT increase yet
3. Login as parent and approve it
4. Login back as child
5. Check total points - should now include approved task
6. ✅ PASS if points added after approval

### 5. Data Persistence Tests

#### Test 5.1: Refresh Page
1. Complete some tasks
2. Refresh the browser page
3. ✅ PASS if completed tasks remain completed

#### Test 5.2: Logout/Login
1. Complete tasks as child
2. Logout
3. Login again as same child
4. ✅ PASS if progress is saved

### 6. Rewards Tests

#### Test 6.1: View Rewards
1. Login as child
2. Scroll to "Available Rewards" section
3. ✅ PASS if rewards display with icons and costs

#### Test 6.2: Check Parent Rewards View
1. Login as parent
2. Click "Rewards" tab
3. ✅ PASS if all family rewards are listed

### 7. Browser Tests

#### Test 7.1: Multiple Tabs
1. Open app in 2 browser tabs
2. Login to both
3. Complete task in one tab
4. Refresh other tab
5. ✅ PASS if state syncs

#### Test 7.2: Incognito Mode
1. Open incognito window
2. Navigate to app
3. Should require login
4. ✅ PASS if not auto-logged in

### 8. Error Handling Tests

#### Test 8.1: Complete Same Task Twice
1. Complete a task
2. Try to complete it again (refresh and try)
3. ✅ PASS if error: "Task already completed today"

#### Test 8.2: Invalid Login
1. Try login with wrong password
2. ✅ PASS if shows error message

### 9. API Endpoint Tests

Run these commands to verify API:

```bash
# Health check
curl http://localhost:8000/health

# Get tasks (while logged in - check browser cookies)
curl http://localhost:8000/api/tasks/ -H "Cookie: access_token=YOUR_TOKEN"
```

## Known Working Features ✅

1. JWT authentication with cookies
2. Task assignment system
3. Task completion (with and without approval)
4. Approval workflow (create → approve/deny → award points)
5. Points tracking (total lifetime points)
6. Daily progress tracking
7. Rewards display
8. Parent and child role separation
9. Family-based data isolation
10. PostgreSQL database persistence

## What to Look For

### Success Indicators:
- ✅ Smooth navigation between pages
- ✅ Tasks load quickly
- ✅ No console errors in browser DevTools
- ✅ Points update correctly
- ✅ Approvals appear in parent dashboard
- ✅ Database persists data across sessions

### Red Flags:
- ❌ Console errors in browser
- ❌ "Failed to complete task" messages
- ❌ Tasks not loading
- ❌ Approval buttons not working
- ❌ Points not updating

## Testing Results

Fill in as you test:

- [ ] Test 1.1: Admin Login
- [ ] Test 1.2: Child Login
- [ ] Test 2.1: View Tasks
- [ ] Test 2.2: Complete Regular Task
- [ ] Test 2.3: Complete Approval Task
- [ ] Test 3.1: View Pending Approvals
- [ ] Test 3.2: Approve Task
- [ ] Test 3.3: Deny Task
- [ ] Test 4.1: Points Tracking
- [ ] Test 4.2: Approval Points
- [ ] Test 5.1: Page Refresh
- [ ] Test 5.2: Logout/Login
- [ ] Test 6.1: View Rewards
- [ ] Test 6.2: Parent Rewards View
- [ ] Test 7.1: Multiple Tabs
- [ ] Test 7.2: Incognito Mode
- [ ] Test 8.1: Duplicate Completion
- [ ] Test 8.2: Invalid Login

## If All Tests Pass → Ready to Deploy! 🚀

Once you've verified everything works locally, you're ready to push to GitHub and deploy to Render.com!

