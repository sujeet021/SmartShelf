from app.services.threshold_service import recalc_all_thresholds,compute_threshold_for_inventory
from app.db.base import AsyncSessionLocal
from app.db.models import Inventory
from app.services.restock_service import check_and_create_restock_for_inventory

async def recalc_thresholds_job():
    try:
        await recalc_all_thresholds()
        print('Thresholds recalculated')
    except Exception as e:
        print('Error in recalc job', e)

async def check_low_stock_job():
    async with AsyncSessionLocal() as session:
        q = await session.execute(Inventory.__table__.select())
        rows = q.fetchall()
        for r in rows:
            inv_id = r._mapping['id']
            q2 = await session.execute(Inventory.__table__.select().where(Inventory.id==inv_id))
            inv = q2.scalars().first()
            if inv.quantity < inv.threshold:
                await check_and_create_restock_for_inventory(inv)