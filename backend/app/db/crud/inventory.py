from sqlalchemy import select
from app.db.models import Inventory


async def get_inventory_by_id(session, inventory_id: int):
    q = await session.execute(select(Inventory).where(Inventory.id == inventory_id))
    inventory = q.scalars().first()
    print(f"get_inventory_by_id: Found inventory for id {inventory_id}: {inventory}")
    return inventory


async def get_inventory_by_item_area(session, item_id, area_id):
    q = await session.execute(select(Inventory).where(
        Inventory.item_id == item_id,
        Inventory.area_id == area_id
    ))
    inventory = q.scalars().first()
    print(f"get_inventory_by_item_area: Found inventory for item {item_id} and area {area_id}: {inventory}")
    return inventory


async def create_inventory(session, inv_in):
    inv = Inventory(**inv_in.model_dump()) 
    session.add(inv)
    await session.flush()
    await session.refresh(inv)
    await session.commit()
    print(f"create_inventory: Created inventory {inv}")
    return inv


async def adjust_inventory_quantity(session, inventory_id: int, delta: int):
    inventory = await get_inventory_by_id(session, inventory_id)
    
    if not inventory:
        print(f"adjust_inventory_quantity: Inventory id {inventory_id} not found")
        return None
        
    inventory.quantity += delta
    await session.flush()
    await session.refresh(inventory)
    await session.commit()
    print(f"adjust_inventory_quantity: Adjusted inventory {inventory_id} by {delta}, new quantity {inventory.quantity}")
    return inventory


async def list_low_stock(session, limit=100):
    q = await session.execute(
        select(Inventory).where(Inventory.quantity < Inventory.threshold).limit(limit)
    )
    low_stock_items = q.scalars().all()
    print(f"list_low_stock: Found {len(low_stock_items)} low stock items")
    return low_stock_items
