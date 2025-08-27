import os
from typing import AsyncGenerator
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import create_async_engine, AsyncConnection
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class DatabaseSettings(BaseSettings):
    """Database configuration settings."""
    
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./patient_appointments.db")
    DB_ECHO: bool = os.getenv("DB_ECHO", "false").lower() in ("true", "1", "yes", "on")


# Settings for database connection
settings = DatabaseSettings()

# Async Database engine for runtime operations
async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DB_ECHO,
    future=True
)


# Metadata for table definitions
metadata = MetaData()


async def get_db_connection() -> AsyncGenerator[AsyncConnection, None]:
    """
    Get database connection 
    """
    async with async_engine.begin() as connection:
        yield connection


async def get_db_connection_autocommit() -> AsyncGenerator[AsyncConnection, None]:
    """
    Get database connection with autocommit
    """
    async with async_engine.connect() as connection:
        yield connection
