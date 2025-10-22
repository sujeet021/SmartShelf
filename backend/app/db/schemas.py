from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class AlertRead(BaseModel):
    id: int
    inventory_id: int
    item_id: int
    area_id: int
    type: str
    created_at: datetime
    resolved: bool
    resolved_at: Optional[datetime]
    payload: Optional[dict]

    model_config = ConfigDict(from_attributes=True)


class RestockOrderRead(BaseModel):
    id: int
    inventory_id: int
    item_id: int
    area_id: int
    quantity_requested: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime]
    expected_delivery_date: Optional[datetime]
    external_ref: Optional[str]

    model_config = ConfigDict(from_attributes=True)


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