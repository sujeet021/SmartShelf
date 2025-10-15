from fastapi import APIRouter, Depends, HTTPException
from app.db.base import AsyncSessionLocal
from app.db.models import RestockOrder
router = APIRouter()

async def get_session():
    async with AsyncSessionLocal() as s:
        yield s

@router.get('/')
async def list_restocks(session=Depends(get_session)):
    q = await session.execute(RestockOrder.__table__.select().order_by(RestockOrder.created_at.desc()).limit)
    return [dict(r) for r in q.fetchall()]