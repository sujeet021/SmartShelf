from sqlalchemy import select
from app.db.models import Order, OrderLine, Inventory
from app.db.base import AsyncSessionLocal

async def create_order(session, order_in):
# order_in: OrderCreate Pydantic
    order = Order(order_reference=order_in.order_reference,
    area_id=order_in.area_id)
    session.add(order)
    await session.flush()
    for line in order_in.lines:
        ol = OrderLine(order_id=order.id, item_id=line.item_id,
        quantity=line.quantity)
        session.add(ol)
# decrease inventory for item/area
        q = await session.execute(
            select(Inventory).where(Inventory.item_id==line.item_id,
            nventory.area_id==order_in.area_id).with_for_update())
        inv = q.scalars().first()
        if inv is None:
            raise Exception(f"No inventory for item {line.item_id} in area{order_in.area_id}")
        if inv.quantity < line.quantity:
            raise Exception(f"Insufficient stock for item {line.item_id}")
        
        inv.quantity = inv.quantity - line.quantity
        session.add(inv)
        await session.flush()
        await session.refresh(order)
        return order

async def get_order(session, order_id):
    q = await session.execute(select(Order).where(Order.id==order_id))
    return q.scalars().first()