"""
Character unlock API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Dict
from app.database import get_db
from app.models.profile import Profile
from app.models.character_unlock import CharacterUnlock
from app.models.task_completion import TaskCompletion
from app.core.dependencies import get_current_user

router = APIRouter()


def check_unlock_requirement(requirement: str, profile: Profile, db: Session) -> bool:
    """
    Check if a profile meets an unlock requirement

    Args:
        requirement: Unlock requirement string (e.g., 'streak_3', 'points_500', 'tasks_25')
        profile: User profile to check
        db: Database session

    Returns:
        True if requirement is met, False otherwise
    """
    if requirement is None:
        return True  # No requirement means always unlocked

    # Parse requirement
    parts = requirement.split('_')
    if len(parts) != 2:
        return False

    req_type, req_value = parts[0], int(parts[1])

    # Check streak requirements
    if req_type == 'streak':
        return profile.current_streak >= req_value

    # Check points requirements
    elif req_type == 'points':
        return profile.total_lifetime_points >= req_value

    # Check task completion requirements
    elif req_type == 'tasks':
        total_tasks = db.query(TaskCompletion).filter(
            TaskCompletion.child_id == profile.id
        ).count()
        return total_tasks >= req_value

    # Check kindness acts (tasks with 'kindness' in description or title)
    elif req_type == 'kindness':
        from app.models.task import Task
        from app.models.task_assignment import TaskAssignment

        kindness_tasks = db.query(TaskCompletion).join(
            Task, TaskCompletion.task_id == Task.id
        ).filter(
            TaskCompletion.child_id == profile.id,
            (Task.title.ilike('%kindness%') | Task.description.ilike('%kindness%'))
        ).count()
        return kindness_tasks >= req_value

    return False


@router.get("/available")
async def get_available_characters(
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all characters for the current user's theme with unlock status
    Returns list of characters with:
    - name, emoji, color, imageUrl, description
    - unlocked: boolean
    - unlockRequirement: string or null
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    # This would normally load from themes.js, but for the API we'll need to
    # duplicate the data or load it dynamically. For now, return a simple structure
    # that the frontend can merge with themes.js data

    # Get all unlocked characters for this user
    unlocked_characters = db.query(CharacterUnlock).filter(
        CharacterUnlock.child_id == current_user.id
    ).all()

    unlocked_keys = {unlock.character_key for unlock in unlocked_characters}

    return {
        "theme": current_user.theme,
        "unlocked_character_keys": list(unlocked_keys)
    }


@router.post("/check-unlocks")
async def check_and_unlock_characters(
    theme_characters: Dict,
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Check if user meets any unlock requirements and unlock eligible characters

    Request body should contain:
    {
        "theme": "minecraft",
        "characters": [
            {"name": "Steve", "character_key": "minecraft_steve", "unlockRequirement": null},
            {"name": "Creeper", "character_key": "minecraft_creeper", "unlockRequirement": "streak_3"}
        ]
    }

    Returns:
    {
        "newly_unlocked": ["minecraft_creeper"],
        "all_unlocked": ["minecraft_steve", "minecraft_alex", "minecraft_creeper"]
    }
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    theme = theme_characters.get("theme")
    characters = theme_characters.get("characters", [])

    # Get currently unlocked characters
    existing_unlocks = db.query(CharacterUnlock).filter(
        CharacterUnlock.child_id == current_user.id,
        CharacterUnlock.theme_key == theme
    ).all()

    existing_keys = {unlock.character_key for unlock in existing_unlocks}
    newly_unlocked = []

    # Check each character's unlock requirement
    for char in characters:
        character_key = char.get("character_key")
        unlock_req = char.get("unlockRequirement")

        # Skip if already unlocked
        if character_key in existing_keys:
            continue

        # Check if requirement is met
        if check_unlock_requirement(unlock_req, current_user, db):
            # Create unlock record
            new_unlock = CharacterUnlock(
                child_id=current_user.id,
                character_key=character_key,
                theme_key=theme,
                unlocked_at=datetime.utcnow(),
                unlock_method=unlock_req if unlock_req else "default"
            )
            db.add(new_unlock)
            newly_unlocked.append(character_key)
            existing_keys.add(character_key)

    if newly_unlocked:
        db.commit()

    return {
        "newly_unlocked": newly_unlocked,
        "all_unlocked": list(existing_keys)
    }


@router.get("/unlocked")
async def get_unlocked_characters(
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get list of all unlocked characters for the current user
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    unlocks = db.query(CharacterUnlock).filter(
        CharacterUnlock.child_id == current_user.id
    ).all()

    return {
        "unlocked_characters": [
            {
                "character_key": unlock.character_key,
                "theme_key": unlock.theme_key,
                "unlocked_at": unlock.unlocked_at.isoformat(),
                "unlock_method": unlock.unlock_method
            }
            for unlock in unlocks
        ]
    }


@router.post("/initialize-defaults")
async def initialize_default_characters(
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Initialize default unlocked characters (those with unlockRequirement: null)
    for the current user's theme. This should be called once when a user first
    selects a theme or when the character system is first enabled.

    Request body should contain:
    {
        "theme": "minecraft",
        "default_characters": ["minecraft_steve", "minecraft_alex"]
    }
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    # This endpoint would be called from the frontend with the list of
    # default characters for the current theme
    return {"message": "Default characters initialized"}
