from app.db.models import RestockOrder, Alert, Inventory
from sqlalchemy import select
from app.db.base import AsyncSessionLocal

async def check_and_create_restock_for_inventory(inv):
    async with AsyncSessionLocal() as session:
# reload inventory
        q = await session.execute(select(Inventory).where(Inventory.id==inv.id))
        inventory = q.scalars().first()
        if inventory.quantity >= inventory.threshold:
            return None
# check active restock
        q2 = await session.execute(select(RestockOrder).where(RestockOrder.inventory_id==inventory.id,
            RestockOrder.status != 'received'))
        active = q2.scalars().first()
        if active:
            return active
# create alert
        alert = Alert(inventory_id=inventory.id, item_id=inventory.item_id,
        area_id=inventory.area_id, type='low_stock', payload={"quantity":inventory.quantity, "threshold": inventory.threshold})
        session.add(alert)
        await session.flush()
# create restock order
        qty_req = max(inventory.threshold - inventory.quantity,inventory.threshold)
        ro = RestockOrder(inventory_id=inventory.id,
item_id=inventory.item_id, area_id=inventory.area_id,quantity_requested=qty_req)
        session.add(ro)
        await session.commit()
        await session.refresh(ro)
        return ro