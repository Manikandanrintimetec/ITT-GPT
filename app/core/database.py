from sqlalchemy import create_engine, text, pool
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from fastapi import HTTPException

from app.core.config import settings
from app.core.logging import logger


engine = create_engine(
    settings.DATABASE_URL,
    poolclass=pool.QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600,
    pool_pre_ping=True,
    echo=False
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    except HTTPException:
        # Don't log HTTP exceptions as database errors
        raise
    except Exception as e:
        logger.error(f"Database session error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


def initialize_database():
    try:
        # Only create tables if they don't exist (preserve existing data)
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")

        with engine.connect() as connection:
            connection.execute(
                text("ALTER TABLE messages ADD COLUMN IF NOT EXISTS provider VARCHAR")
            )
            connection.commit()
        logger.info("Database schema initialized")
    except Exception as e:
        logger.error(f"Database initialization error: {str(e)}")
        raise