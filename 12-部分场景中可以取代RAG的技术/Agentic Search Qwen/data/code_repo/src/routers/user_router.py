"""用户路由"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from services.user_service import UserService
from schemas.user import UserCreate, UserUpdate, UserResponse

user_router = APIRouter()

@user_router.get("/", response_model=list[UserResponse])
def list_users(department: str = None, skip: int = 0, limit: int = 20,
               db: Session = Depends(get_db)):
    service = UserService(db)
    return service.list_users(department=department, skip=skip, limit=limit)

@user_router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    service = UserService(db)
    user = service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@user_router.post("/", response_model=UserResponse)
def create_user(data: UserCreate, db: Session = Depends(get_db)):
    service = UserService(db)
    return service.create_user(data)

@user_router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, data: UserUpdate, db: Session = Depends(get_db)):
    service = UserService(db)
    user = service.update_user(user_id, data)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
