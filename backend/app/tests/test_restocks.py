import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.main import app
from app.db.models import Base, Inventory, Item, Area, RestockOrder


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
async def test_list_restocks(db_session):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        async with db_session() as session:
            # Create Area, Item, and Inventory
            area = Area(name="TestArea")
            item = Item(sku="SKU1", name="TestItem")
            session.add_all([area, item])
            await session.flush()
            await session.refresh(area)
            await session.refresh(item)
            inventory = Inventory(item_id=item.id, area_id=area.id, quantity=50, threshold=10)
            session.add(inventory)
            await session.commit()

            # Add a restock order manually to DB (simulate existing data)
            restock_order = RestockOrder(
                inventory_id=inventory.id,
                item_id=item.id,
                area_id=area.id,
                quantity_requested=20,
                status="requested"
            )
            session.add(restock_order)
            await session.commit()

        # Test fetching restock orders
        resp = await ac.get("/api/v1/restocks/")
        assert resp.status_code == 200
        restocks = resp.json()
        assert len(restocks) > 0
        assert restocks[0]["quantity_requested"] == 20
        assert restocks[0]["status"] == "requested"
