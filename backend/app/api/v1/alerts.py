from fastapi import APIRouter, Depends
from app.db.base import AsyncSessionLocal
from app.db.models import Alert

router = APIRouter()

async def get_session():
    async with AsyncSessionLocal() as s:
        yield s

@router.get('/')
async def list_alerts(session=Depends(get_session)):
    q = await session.execute(Alert.__table__.select().order_by(Alert.created_at.desc()).limit(100))
    return [dict(r) for r in q.fetchall()]