from fastapi import APIRouter, Depends, HTTPException
from app.db.base import AsyncSessionLocal
from app.db.schemas import ItemCreate, ItemRead
from app.db.crud.items import create_item, list_items, get_item


router = APIRouter(tags=["Items"])  # Removed prefix here


async def get_session():
    async with AsyncSessionLocal() as session:
        yield session


@router.post("/", response_model=ItemRead)
async def create_item_route(item_in: ItemCreate, session=Depends(get_session)):
    item = await create_item(session, item_in)
    return item


@router.get("/", response_model=list[ItemRead])
async def list_items_route(session=Depends(get_session)):
    return await list_items(session)


@router.get("/{item_id}", response_model=ItemRead)
async def get_item_route(item_id: int, session=Depends(get_session)):
    item = await get_item(session, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.put("/{item_id}", response_model=ItemRead)
async def update_item_route(item_id: int, item_update: dict, session=Depends(get_session)):
    from app.db.models import Item
    from sqlalchemy import select
    
    result = await session.execute(select(Item).where(Item.id == item_id))
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Update fields if provided
    if 'sku' in item_update:
        item.sku = item_update['sku']
    if 'name' in item_update:
        item.name = item_update['name']
    if 'category' in item_update:
        item.category = item_update['category']
    if 'unit' in item_update:
        item.unit = item_update['unit']
    
    await session.commit()
    await session.refresh(item)
    return ItemRead.model_validate(item)

@router.delete("/{item_id}")
async def delete_item_route(item_id: int, session=Depends(get_session)):
    from app.db.models import Item
    from sqlalchemy import select, delete
    
    result = await session.execute(select(Item).where(Item.id == item_id))
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    await session.execute(delete(Item).where(Item.id == item_id))
    await session.commit()
    return {"message": "Item deleted successfully"}
