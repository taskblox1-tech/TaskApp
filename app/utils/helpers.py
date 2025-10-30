"""
Utility helper functions
"""
import random
import string
from datetime import date, timedelta


def generate_join_code(length: int = 8) -> str:
    """Generate a random join code for families"""
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


def get_week_bounds(target_date: date = None) -> tuple:
    """
    Get Friday-to-Thursday week bounds for a given date
    Returns (start_friday, end_thursday)
    """
    if target_date is None:
        target_date = date.today()
    
    # Find the most recent Friday (or today if it's Friday)
    days_since_friday = (target_date.weekday() - 4) % 7
    start_friday = target_date - timedelta(days=days_since_friday)
    
    # End is the following Thursday
    end_thursday = start_friday + timedelta(days=6)
    
    return start_friday, end_thursday


def is_school_day(check_date: date = None) -> bool:
    """Check if a date is a school day (Monday-Friday)"""
    if check_date is None:
        check_date = date.today()
    return check_date.weekday() < 5  # 0-4 = Mon-Fri


def is_weekend(check_date: date = None) -> bool:
    """Check if a date is a weekend (Saturday-Sunday)"""
    if check_date is None:
        check_date = date.today()
    return check_date.weekday() >= 5  # 5-6 = Sat-Sun


def points_emoji(points: int) -> str:
    """Get emoji based on points value"""
    if points >= 100:
        return "💎"
    elif points >= 50:
        return "🌟"
    elif points >= 25:
        return "⭐"
    elif points >= 10:
        return "✨"
    else:
        return "🔹"