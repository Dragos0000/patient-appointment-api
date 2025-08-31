import asyncio
from src.adapters.database.connection import async_engine, metadata
import src.adapters.database.tables


async def create_tables():
    """Create all database tables."""
    async with async_engine.begin() as conn:
        await conn.run_sync(metadata.create_all)


async def drop_tables():
    """Drop all database tables."""
    async with async_engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)


async def reset_database():
    """Drop and recreate all database tables."""
    await drop_tables()
    await create_tables()


if __name__ == "__main__":
    # Run table creation when script is executed directly
    asyncio.run(create_tables())
    print("Database tables created successfully!")
