import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.main import app
from app.db.models import Base, Area, Item, Inventory

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
async def test_create_and_get_order(db_session):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        async with db_session() as session:
            # Create Area and Item
            area = Area(name="TestArea")
            item = Item(sku="SKU1", name="TestItem")
            session.add_all([area, item])
            await session.flush()
            await session.refresh(area)
            await session.refresh(item)

            # Create inventory record for item in the area
            inventory = Inventory(item_id=item.id, area_id=area.id, quantity=100, threshold=10)
            session.add(inventory)
            await session.commit()

        # Prepare order data
        order_data = {
            "order_reference": "Order001",
            "area_id": area.id,
            "lines": [
                {"item_id": item.id, "quantity": 5}
            ]
        }

        # Create order
        post_resp = await ac.post("/api/v1/orders/", json=order_data)
        assert post_resp.status_code == 200
        created_order = post_resp.json()
        assert created_order["order_reference"] == order_data["order_reference"]
        assert created_order["area_id"] == area.id

        order_id = created_order["id"]

        # Get order by id
        get_resp = await ac.get(f"/api/v1/orders/{order_id}")
        assert get_resp.status_code == 200
        fetched_order = get_resp.json()
        assert fetched_order["id"] == order_id
        assert fetched_order["order_reference"] == order_data["order_reference"]

        # Check inventory was reduced
        async with db_session() as session:
            inv = await session.get(Inventory, inventory.id)
            assert inv.quantity == 95  # 100 - 5 ordered
