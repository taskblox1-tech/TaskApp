"""
FastAPI dependencies for authentication and authorization
"""
from typing import Optional
from fastapi import Depends, HTTPException, status, Cookie
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.security import decode_access_token
from app.models.profile import Profile


async def get_current_user(
    access_token: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
) -> Optional[Profile]:
    """Get the current authenticated user from JWT token in cookie"""
    import logging
    logger = logging.getLogger(__name__)

    logger.info(f"get_current_user called. Cookie received: {access_token is not None}")

    if not access_token:
        logger.warning("No access_token cookie found")
        return None

    try:
        # Decode token
        payload = decode_access_token(access_token)
        if payload is None:
            logger.warning("Token decode returned None")
            return None

        user_id_str = payload.get("sub")
        logger.info(f"Decoded token, user_id (string): {user_id_str}")

        if user_id_str is None:
            logger.warning("No user_id in token payload")
            return None

        # Convert string back to int
        user_id = int(user_id_str)
        logger.info(f"Converted user_id to int: {user_id}")
    except Exception as e:
        logger.error(f"Error decoding token: {e}")
        return None

    # Get user from database
    user = db.query(Profile).filter(Profile.id == user_id).first()
    logger.info(f"User found in database: {user is not None}")
    return user