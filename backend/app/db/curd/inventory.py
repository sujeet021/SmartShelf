from sqlalchemy import select, update
from app.db.models import Inventory




async def get_inventory_by_item_area(session, item_id, area_id):
    q = await session.execute(select(Inventory).where(Inventory.item_id==item_