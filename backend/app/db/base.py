
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings


async_engine = create_async_engine(settings.DATABASE_URL, echo=False, future=True)
AsyncSessionLocal = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()


print("Connecting to DB:", settings.DATABASE_URL)


async def init_db():
    print("Running DB create_all()")
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("DB tables created or confirmed")


print("Connecting to DB:", settings.DATABASE_URL)
