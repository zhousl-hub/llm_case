"""合同模型"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.sql import func
from database import Base

class Contract(Base):
    __tablename__ = "contracts"
    id = Column(Integer, primary_key=True, index=True)
    client_name = Column(String(200), nullable=False)
    type = Column(String(50))
    amount = Column(Float, default=0)
    status = Column(String(20), default="pending")
    sign_date = Column(DateTime)
    expire_date = Column(DateTime)
    responsible_person = Column(String(50))
    description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
