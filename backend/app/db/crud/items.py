from sqlalchemy import select
from app.db.models import Item

# Create new item
async def create_item(session, item_in):
    item = Item(**item_in.dict())
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item

# Get single item
async def get_item(session, item_id: int):
    result = await session.execute(select(Item).where(Item.id == item_id))
    return result.scalars().first()

# List all items
async def list_items(session, skip=0, limit=100):
    result = await session.execute(select(Item).offset(skip).limit(limit))
    return result.scalars().all()
