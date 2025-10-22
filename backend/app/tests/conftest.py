import pytest
from app.db.base import async_engine, Base
import asyncio

@pytest.fixture(scope="module", autouse=True)
def event_loop():
    """Create an event loop for async tests (module-scope)."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="module")
async def initialized_db():
    # create tables fresh for test
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    # teardown
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
