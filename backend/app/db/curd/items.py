from sqlalchemy import select
from app.db.models import Item
from app.db.base import AsyncSessionLocal




async def create_item(session, item_in):
    item = Item(**item_in.dict())
    session.add(item)
    await session.flush()
    await session.refresh(item)
    return item




async def get_item(session, item_id: int):
    q = await session.execute(select(Item).where(Item.id==item_id))
    return q.scalars().first()




async def list_items(session, skip=0, limit=100):
    q = await session.execute(select(Item).offset(skip).limit(limit))
    return q.scalars().all()