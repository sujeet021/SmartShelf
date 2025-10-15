from sqlalchemy import select, update
from app.db.models import Inventory
async def get_inventory_by_item_area(session, item_id, area_id):
    q = await session.execute(select(Inventory).where(Inventory.item_id==item_id,
    Inventory.area_id==area_id))
    return q.scalars().first()
async def create_inventory(session, inv_in):
    inv = Inventory(**inv_in.dict())
    session.add(inv)
    await session.flush()
    await session.refresh(inv)
    return inv
async def update_inventory_quantity(session, inventory: Inventory, delta:
int):
    inventory.quantity = inventory.quantity + delta
    await session.flush()
    await session.refresh(inventory)
    return inventory
async def list_low_stock(session, limit=100):
    q = await session.execute(select(Inventory).where(Inventory.quantity <
    Inventory.threshold).limit(limit))
    return q.scalars().all()