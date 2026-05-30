"""产品模型"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.sql import func
from database import Base

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    category = Column(String(50))
    price = Column(Float, default=0)
    stock = Column(Integer, default=0)
    description = Column(Text)
    launch_date = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
