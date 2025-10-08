from fastapi import FastAPI
from routes import product_routes, transaction_routes

app = FastAPI(title="Real-Time Inventory Tracker")

# Register routes
app.include_router(product_routes.router, prefix="/products")
app.include_router(transaction_routes.router, prefix="/transactions")

@app.get("/")
def home():
    return {"msg": "Real-Time Inventory API running"}
