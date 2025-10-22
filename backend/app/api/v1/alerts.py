from fastapi import APIRouter, Depends
from sqlalchemy import select
from app.db.base import AsyncSessionLocal
from app.db.models import Alert
from app.db.schemas import AlertRead  # You'll create this next

router = APIRouter()

async def get_session():
    async with AsyncSessionLocal() as session:
        yield session

@router.get('/', response_model=list[AlertRead])
async def list_alerts(session=Depends(get_session)):
    q = await session.execute(
        select(Alert).order_by(Alert.created_at.desc()).limit(100)
    )
    alerts = q.scalars().all()
    return [AlertRead.model_validate(alert) for alert in alerts]

@router.get('/unresolved', response_model=list[AlertRead])
async def get_unresolved_alerts(session=Depends(get_session)):
    q = await session.execute(
        select(Alert).where(Alert.resolved == False).order_by(Alert.created_at.desc())
    )
    alerts = q.scalars().all()
    return [AlertRead.model_validate(alert) for alert in alerts]

@router.put('/{alert_id}/resolve')
async def resolve_alert(alert_id: int, session=Depends(get_session)):
    from sqlalchemy import update
    from datetime import datetime
    
    await session.execute(
        update(Alert)
        .where(Alert.id == alert_id)
        .values(resolved=True, resolved_at=datetime.utcnow())
    )
    await session.commit()
    return {"message": "Alert resolved successfully"}

@router.delete('/{alert_id}')
async def delete_alert(alert_id: int, session=Depends(get_session)):
    from sqlalchemy import delete
    
    await session.execute(delete(Alert).where(Alert.id == alert_id))
    await session.commit()
    return {"message": "Alert deleted successfully"}
