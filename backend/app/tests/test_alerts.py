import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.main import app
from app.db.models import Base, Alert, Inventory, Item, Area

@pytest.fixture
async def db_session():
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
async def test_list_alerts(db_session):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        async with db_session() as session:
            area = Area(name="TestArea")
            item = Item(sku="SKU1", name="TestItem")
            inventory = Inventory(item_id=item.id, area_id=area.id, quantity=10, threshold=5)
            session.add_all([area, item, inventory])
            await session.flush()
            await session.refresh(area)
            await session.refresh(item)
            await session.refresh(inventory)

            alert = Alert(
                inventory_id=inventory.id,
                item_id=item.id,
                area_id=area.id,
                type="test_alert",
                resolved=False,
                payload={"info": "Test payload"}
            )
            session.add(alert)
            await session.commit()

        resp = await ac.get("/api/v1/alerts/")
        assert resp.status_code == 200
        alerts = resp.json()
        assert len(alerts) == 1
        assert alerts[0]["type"] == "test_alert"
        assert alerts[0]["resolved"] is False
