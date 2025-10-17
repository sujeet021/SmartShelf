from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Enum, JSON, UniqueConstraint
category = Column(String, nullable=True)
unit = Column(String, default='pcs')
created_at = Column(DateTime(timezone=True), server_default=func.now())




class Inventory(Base):
    __tablename__ = 'inventory'
    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey('items.id'), nullable=False)
    area_id = Column(Integer, ForeignKey('areas.id'), nullable=False)
    quantity = Column(Integer, nullable=False, default=0)
    threshold = Column(Integer, nullable=False, default=0)
    safety_stock = Column(Integer, default=0)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    __table_args__ = (UniqueConstraint('item_id', 'area_id', name='uix_item_area'),)


item = relationship('Item')
area = relationship('Area')




class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True, index=True)
    order_reference = Column(String, unique=True, nullable=True)
    area_id = Column(Integer, ForeignKey('areas.id'), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(Enum(OrderStatus), default=OrderStatus.placed)
    metadata = Column(JSON, nullable=True)


area = relationship('Area')
lines = relationship('OrderLine', back_populates='order')




class OrderLine(Base):
    __tablename__ = 'order_lines'
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    item_id = Column(Integer, ForeignKey('items.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Integer, nullable=True)


order = relationship('Order', back_populates='lines')
item = relationship('Item')




class Alert(Base):
    __tablename__ = 'alerts'
    id = Column(Integer, primary_key=True, index=True)
    inventory_id = Column(Integer, ForeignKey('inventory.id'), nullable=False)
    item_id = Column(Integer, nullable=False)
    area_id = Column(Integer, nullable=False)
    type = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    payload = Column(JSON, nullable=True)




class RestockOrder(Base):
    __tablename__ = 'restock_orders'
    id = Column(Integer, primary_key=True, index=True)
    inventory_id = Column(Integer, ForeignKey('inventory.id'), nullable=False)
    item_id = Column(Integer, nullable=False)
    area_id = Column(Integer, nullable=False)
    quantity_requested = Column(Integer, nullable=False)
    status = Column(Enum(RestockStatus), default=RestockStatus.requested)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    expected_delivery_date = Column(DateTime(timezone=True), nullable=True)
    external_ref = Column(String, nullable=True)