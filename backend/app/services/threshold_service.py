from app.core.config import settings
from sqlalchemy import select, func
from app.db.models import OrderLine, Order, Inventory
from app.db.base import AsyncSessionLocal
async def compute_threshold_for_inventory(session, inventory):
# simple avg daily demand over last D days (uses orders/order_lines)
# For simplicity this uses a naive aggregation on OrderLine by date; for
#production use an aggregated table
    days = settings.THRESHOLD_LOOKBACK_DAYS
    q = await session.execute(select(func.sum(OrderLine.quantity)).join(Order,
        OrderLine.order_id==Order.id).where(Order.area_id==inventory.area_id)
    )
    total = q.scalar() or 0
    avg_daily = total / max(days, 1)
    threshold = int((avg_daily * settings.LEAD_TIME_DAYS *settings.SAFETY_FACTOR) + inventory.safety_stock)
    if threshold < 1:
        threshold = 1
    return threshold

async def recalc_all_thresholds():
    async with AsyncSessionLocal() as session:
        q = await session.execute(select(Inventory))
        invs = q.scalars().all()
        for inv in invs:
            new_th = await compute_threshold_for_inventory(session, inv)
            inv.threshold = new_th
            session.add(inv)
        await session.commit()
