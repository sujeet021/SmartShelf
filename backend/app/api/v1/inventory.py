from fastapi import APIRouter, Depends, HTTPException
from app.db.schemas import InventoryCreate, InventoryRead
from app.db.base import AsyncSessionLocal
from app.db.crud.inventory import create_inventory,get_inventory_by_item_area,update_inventory_quantity, list_low_stock

router = APIRouter()

async def get_session():
    async with AsyncSessionLocal() as s:
        yield s

@router.post('/', response_model=InventoryRead)
async def create_inventory_endpoint(inv_in: InventoryCreate,
session=Depends(get_session)):
    existing = await get_inventory_by_item_area(session, inv_in.item_id,inv_in.area_id)
    if existing:
        raise HTTPException(status_code=400, detail='Inventory row alreadyexists')
    inv = await create_inventory(session, inv_in)
    return InventoryRead.from_orm(inv)

@router.get('/low-stock', response_model=list[InventoryRead])
async def low_stock(session=Depends(get_session)):
    invs = await list_low_stock(session)
    return [InventoryRead.from_orm(i) for i in invs]