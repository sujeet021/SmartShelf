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
    
    # Return all inventory records
    from app.db.models import Inventory
    from sqlalchemy import select
    
    result = await session.execute(select(Inventory).order_by(Inventory.id))
    inventory = result.scalars().all()
    return [InventoryRead.model_validate(inv) for inv in inventory]

@router.get('/low-stock', response_model=list[InventoryRead])
async def get_low_stock(session=Depends(get_session)):
    invs = await list_low_stock(session)
    return [InventoryRead.model_validate(i) for i in invs]

@router.put('/{inventory_id}', response_model=InventoryRead)
async def update_inventory(
    inventory_id: int,
    inventory_update: dict,
    session=Depends(get_session)
):
    # This is a simplified update - you might want to implement proper update logic
    from app.db.models import Inventory
    from sqlalchemy import select
    
    result = await session.execute(select(Inventory).where(Inventory.id == inventory_id))
    inv = result.scalar_one_or_none()
    
    if not inv:
        raise HTTPException(status_code=404, detail='Inventory not found')
    
    # Update fields if provided
    if 'quantity' in inventory_update:
        inv.quantity = inventory_update['quantity']
    if 'threshold' in inventory_update:
        inv.threshold = inventory_update['threshold']
    if 'safety_stock' in inventory_update:
        inv.safety_stock = inventory_update['safety_stock']
    
    await session.commit()
    await session.refresh(inv)
    return InventoryRead.model_validate(inv)
