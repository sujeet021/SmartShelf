from fastapi import APIRouter, Depends, HTTPException
from app.db.schemas import OrderCreate, OrderRead
from app.db.base import AsyncSessionLocal
from app.db.crud.orders import create_order, get_order
router = APIRouter()
async def get_session():
    async with AsyncSessionLocal() as s:
        yield s

@router.post('/', response_model=OrderRead)
async def create_order_endpoint(order_in: OrderCreate,session=Depends(get_session)):
    try:
        order = await create_order(session, order_in)
        return OrderRead.from_orm(order)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get('/{order_id}', response_model=OrderRead)
async def get_order_endpoint(order_id: int, session=Depends(get_session)):
    order = await get_order(session, order_id)
    if not order:
        raise HTTPException(status_code=404, detail='Order not found')
    return OrderRead.from_orm(order)