from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from app.db.base import AsyncSessionLocal
from app.db.models import RestockOrder
from app.db.schemas import RestockOrderRead

router = APIRouter()

async def get_session():
    async with AsyncSessionLocal() as s:
        yield s

@router.get('/', response_model=list[RestockOrderRead])
async def list_restocks(session=Depends(get_session)):
    q = await session.execute(
        select(RestockOrder).order_by(RestockOrder.created_at.desc()).limit(100)
    )
    restocks = q.scalars().all()
    return [RestockOrderRead.model_validate(restock) for restock in restocks]

@router.post('/', response_model=RestockOrderRead)
async def create_restock(restock_data: dict, session=Depends(get_session)):
    try:
        from app.db.models import RestockOrder, RestockStatus
        from datetime import datetime
        
        restock = RestockOrder(
            inventory_id=restock_data.get('inventory_id'),
            item_id=restock_data.get('item_id'),
            area_id=restock_data.get('area_id'),
            quantity_requested=restock_data.get('quantity_requested', 0),
            status=RestockStatus.requested,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        session.add(restock)
        await session.commit()
        await session.refresh(restock)
        
        return RestockOrderRead.model_validate(restock)
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(e))
