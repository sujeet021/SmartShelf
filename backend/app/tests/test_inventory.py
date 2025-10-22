import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.main import app
from app.db.models import Base, Area, Item


@pytest.fixture
async def db_session():
    """Creates an isolated async test DB session using one event loop."""
    engine = create_async_engine(
        "postgresql+asyncpg://akshay:password123@localhost:5432/inventory_db",
        echo=False,
        future=True,
    )
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield async_session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.mark.asyncio
async def test_create_and_adjust_inventory(db_session):
    """End-to-end inventory test using FastAPI + SQLAlchemy Async."""

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        async with db_session() as session:
            # Create area & item directly in DB
            a = Area(name="TestArea")
            i = Item(sku="SKU1", name="TestItem")
            session.add_all([a, i])
            await session.flush()
            await session.refresh(a)
            await session.refresh(i)
            await session.commit()

        # Create inventory
        resp = await ac.post(
            "/api/v1/inventory/",
            json={"item_id": i.id, "area_id": a.id, "quantity": 10, "threshold": 5},
        )
        assert resp.status_code == 200
        data = resp.json()
        inv_id = data["id"]
        assert data["quantity"] == 10

        # Decrement quantity
        resp2 = await ac.patch(f"/api/v1/inventory/{inv_id}/adjust", json={"delta": -7})
        assert resp2.status_code == 200
        data2 = resp2.json()
        assert data2["quantity"] == 3

        # Low stock check
        resp3 = await ac.get("/api/v1/inventory/?low_stock=true")
        assert resp3.status_code == 200
        arr = resp3.json()
        assert any(x["id"] == inv_id for x in arr)
