from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime


# --- Area Schemas ---

class AreaCreate(BaseModel):
    name: str
    city: Optional[str]


class AreaRead(AreaCreate):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True) 


# --- Item Schemas ---

class ItemCreate(BaseModel):
    sku: str
    name: str
    category: Optional[str]
    unit: Optional[str]


class ItemRead(ItemCreate):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# --- Inventory Schemas ---

class InventoryCreate(BaseModel):
    item_id: int
    area_id: int
    quantity: int = 0
    threshold: Optional[int] = 0


class InventoryRead(InventoryCreate):
    id: int
    last_updated: datetime
    model_config = ConfigDict(from_attributes=True)

# ✅ FIXED: The missing schema
class InventoryAdjustment(BaseModel):
    delta: int


# --- Order Schemas ---

class OrderLineCreate(BaseModel):
    item_id: int
    quantity: int


class OrderCreate(BaseModel):
    order_reference: Optional[str]
    area_id: int
    lines: List[OrderLineCreate]


class OrderRead(BaseModel):
    id: int
    order_reference: Optional[str]
    area_id: int
    created_at: datetime
    status: str
    model_config = ConfigDict(from_attributes=True)