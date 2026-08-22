import asyncio
import logging
from app.core.database import engine, Base
from app.models.domain import * # Ensure all models are imported

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("init_db")


async def init_models():
    logger.info("Connecting to PostgreSQL and creating all database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("All tables created successfully!")


if __name__ == "__main__":
    asyncio.run(init_models())
