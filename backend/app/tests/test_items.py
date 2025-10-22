import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.main import app
from app.db.models import Base

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
async def test_create_and_get_item(db_session):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        async with db_session() as session:
            # Create an item using POST /api/v1/items/
            item_data = {
                "sku": "ITEM123",
                "name": "Test Item",
                "category": "Test Category",
                "unit": "pcs"
            }
            post_resp = await ac.post("/api/v1/items/", json=item_data)
            assert post_resp.status_code == 200
            created_item = post_resp.json()
            assert created_item["sku"] == item_data["sku"]
            assert created_item["name"] == item_data["name"]

            item_id = created_item["id"]

            # Get the item by ID using GET /api/v1/items/{item_id}
            get_resp = await ac.get(f"/api/v1/items/{item_id}")
            assert get_resp.status_code == 200
            fetched_item = get_resp.json()
            assert fetched_item["id"] == item_id
            assert fetched_item["sku"] == item_data["sku"]

            # List all items using GET /api/v1/items/
            list_resp = await ac.get("/api/v1/items/")
            assert list_resp.status_code == 200
            items_list = list_resp.json()
            assert any(item["id"] == item_id for item in items_list)
