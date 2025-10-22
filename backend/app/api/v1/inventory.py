from fastapi import APIRouter, Depends, HTTPException, Query
from app.db.schemas import InventoryCreate, InventoryRead, InventoryAdjustment 
from app.db.base import AsyncSessionLocal
from app.db.crud.inventory import (
    create_inventory,
    get_inventory_by_item_area,
    adjust_inventory_quantity, 
    list_low_stock
)

router = APIRouter()

async def get_session():
    async with AsyncSessionLocal() as s:
        yield s

@router.post('/', response_model=InventoryRead)
async def create_inventory_endpoint(inv_in: InventoryCreate, session=Depends(get_session)):
    existing = await get_inventory_by_item_area(session, inv_in.item_id, inv_in.area_id)
    if existing:
        raise HTTPException(status_code=400, detail='Inventory row already exists')
    inv = await create_inventory(session, inv_in)
    return InventoryRead.model_validate(inv)

@router.patch('/{inventory_id}/adjust', response_model=InventoryRead)
async def adjust_inventory_endpoint(
    inventory_id: int,
    adjustment: InventoryAdjustment,
    session=Depends(get_session)
):
    inv = await adjust_inventory_quantity(session, inventory_id, adjustment.delta)
    if not inv:
        raise HTTPException(status_code=404, detail='Inventory not found')
    return InventoryRead.model_validate(inv)

@router.get('/', response_model=list[InventoryRead])
async def list_inventory(session=Depends(get_session), low_stock: bool = Query(False)):
    if low_stock:
        invs = await list_low_stock(session)
        return [InventoryRead.model_validate(i) for i in invs]
    # Implement listing all inventory if needed or return empty list
    return []
