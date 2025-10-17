from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.workers.tasks import recalc_thresholds_job, check_low_stock_job


scheduler = AsyncIOScheduler()
# schedule jobs
scheduler.add_job(recalc_thresholds_job, 'interval', minutes=60, id='recalc_thresholds')
scheduler.add_job(check_low_stock_job, 'interval', minutes=15, id='check_low_stock')