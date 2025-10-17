import asyncio
import pytest
from httpx import AsyncClient
from app.main import app
from app.db.base import async_engine, Base
from app.db.base import AsyncSessionLocal
@pytest.fixture(scope='module')
async def initialized_db():
# create tables
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
# teardown
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.mark.asyncio
async def test_create_and_adjust_inventory(initialized_db):
    async with AsyncClient(app=app, base_url='http://test') as ac:
# create area and item directly using DB session because we don't have endpoints here
        async with AsyncSessionLocal() as s:
            from app.db.models import Area, Item
            a = Area(name='TestArea')
            i = Item(sku='SKU1', name='TestItem')
            s.add_all([a, i])
            await s.flush()
            await s.refresh(a)
            await s.refresh(i)
            area_id = a.id
            item_id = i.id
            await s.commit()
# create inventory
    resp = await ac.post('/api/v1/inventory/', json={"item_id": item_id,
    "area_id": area_id, "quantity": 10, "threshold": 5})
    assert resp.status_code == 200
    data = resp.json()
    inv_id = data['id']
    assert data['quantity'] == 10

# decrement quantity by 7 (should trigger low stock: 3 < threshold 5)
    resp2 = await ac.patch(f'/api/v1/inventory/{inv_id}/adjust',
    json={"delta": -7})
    assert resp2.status_code == 200
    data2 = resp2.json()
    assert data2['quantity'] == 3
    # get low-stock list
    resp3 = await ac.get('/api/v1/inventory/?low_stock=true')
    assert resp3.status_code == 200
    arr = resp3.json()
    assert any(x['id'] == inv_id for x in arr)