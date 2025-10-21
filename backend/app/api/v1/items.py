from fastapi import APIRouter, Depends, HTTPException
from app.db.base import AsyncSessionLocal
from app.db.schemas import InventoryRead, InventoryCreate  # You can create ItemSchema if you want
from app.db.crud.items import create_item, list_items, get_item


router = APIRouter(prefix="/items", tags=["Items"])

async def get_session():
    async with AsyncSessionLocal() as session:
        yield session

@router.post("/")
async def create_item_route(item_in: InventoryCreate, session=Depends(get_session)):
    item = await create_item(session, item_in)
    return item

@router.get("/")
async def list_items_route(session=Depends(get_session)):
    return await list_items(session)

@router.get("/{item_id}")
async def get_item_route(item_id: int, session=Depends(get_session)):
    item = await get_item(session, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item
