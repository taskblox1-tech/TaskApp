import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import engine, Base, init_db
from app.models import *  # Import all models
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Initialize database by creating all tables"""
    try:
        logger.info("🔨 Creating database tables...")
        init_db()
        logger.info("✅ Database initialized successfully!")
        logger.info("📋 Tables created:")
        for table in Base.metadata.tables.keys():
            logger.info(f"   - {table}")
    except Exception as e:
        logger.error(f"❌ Error initializing database: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()