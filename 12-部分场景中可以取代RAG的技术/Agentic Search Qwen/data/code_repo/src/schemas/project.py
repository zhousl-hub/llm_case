"""项目数据模式"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ProjectBase(BaseModel):
    name: str
    department: Optional[str] = None
    lead: Optional[str] = None
    description: Optional[str] = None

class ProjectCreate(ProjectBase):
    status: Optional[str] = "planning"
    budget: Optional[float] = 0
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None
    lead: Optional[str] = None

class ProjectResponse(ProjectBase):
    id: int
    status: str
    budget: float
    created_at: datetime
    class Config:
        from_attributes = True
