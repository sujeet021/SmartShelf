from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.base import async_engine, init_db
from app.api.v1 import auth, items, inventory, orders, alerts, restocks
from app.core.tasks import scheduler


app = FastAPI(title="Inventory Storage Management - Backend")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# include routers
app.include_router(auth.router, prefix="/api/v1/auth")
app.include_router(items.router, prefix="/api/v1/items")
app.include_router(inventory.router, prefix="/api/v1/inventory")
app.include_router(orders.router, prefix="/api/v1/orders")
app.include_router(alerts.router, prefix="/api/v1/alerts")
app.include_router(restocks.router, prefix="/api/v1/restocks")




@app.on_event("startup")
async def startup_event():
# initialize DB (create tables in dev) and start scheduler
    await init_db()
    scheduler.start()




@app.on_event("shutdown")
async def shutdown_event():
    await async_engine.dispose()
    scheduler.shutdown()