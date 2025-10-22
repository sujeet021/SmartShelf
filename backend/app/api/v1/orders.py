from fastapi import APIRouter, Depends, HTTPException
from app.db.schemas import OrderCreate, OrderRead
from app.db.base import AsyncSessionLocal
from app.db.crud.orders import create_order, get_order
router = APIRouter()
async def get_session():
    async with AsyncSessionLocal() as s:
        yield s

@router.post('/', response_model=OrderRead)
async def create_order_endpoint(order_data: dict, session=Depends(get_session)):
    try:
        from app.db.models import Order, OrderLine, OrderStatus
        from datetime import datetime
        
        # Create the order
        order = Order(
            order_reference=order_data.get('order_reference', f'ORD-{datetime.now().strftime("%Y%m%d%H%M%S")}'),
            area_id=order_data.get('area_id'),
            status=OrderStatus.placed,
            created_at=datetime.utcnow()
        )
        session.add(order)
        await session.commit()
        await session.refresh(order)
        
        # Create order lines
        for line_data in order_data.get('order_lines', []):
            order_line = OrderLine(
                order_id=order.id,
                item_id=line_data.get('item_id'),
                quantity=line_data.get('quantity', 1),
                price=line_data.get('price', 0)
            )
            session.add(order_line)
        
        await session.commit()
        await session.refresh(order)
        
        return OrderRead.model_validate(order)
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get('/', response_model=list[OrderRead])
async def list_orders(session=Depends(get_session)):
    from app.db.models import Order
    from sqlalchemy import select
    
    result = await session.execute(select(Order).order_by(Order.created_at.desc()))
    orders = result.scalars().all()
    return [OrderRead.model_validate(order) for order in orders]

@router.get('/{order_id}', response_model=OrderRead)
async def get_order_endpoint(order_id: int, session=Depends(get_session)):
    order = await get_order(session, order_id)
    if not order:
        raise HTTPException(status_code=404, detail='Order not found')
    return OrderRead.model_validate(order)