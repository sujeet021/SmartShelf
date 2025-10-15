from fastapi import APIRouter, Depends, HTTPException
from app.db.schemas import ItemCreate, ItemRead
from app.db.base import AsyncSessionLocal
from app.db.crud.items import create_item, list_items


router = APIRouter()

async def get_session():
    async with AsyncSessionLocal() as s:
        yield s

@router.post('/', response_model=ItemRead)
async def create_item_endpoint(item: ItemCreate,
session=Depends(get_session)):
    db_item = await create_item(session, item)
    return ItemRead.from_orm(db_item)

@router.get('/', response_model=list[ItemRead])
async def list_items_endpoint(session=Depends(get_session)):
    items = await list_items(session)
    return [ItemRead.from_orm(i) for i in items]