"""用户服务"""
from typing import Optional
from sqlalchemy.orm import Session
from models.user import User
from schemas.user import UserCreate, UserUpdate

class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get_user(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def create_user(self, user_data: UserCreate) -> User:
        user = User(**user_data.dict())
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        user = self.get_user(user_id)
        if user:
            for key, value in user_data.dict(exclude_unset=True).items():
                setattr(user, key, value)
            self.db.commit()
            self.db.refresh(user)
        return user

    def delete_user(self, user_id: int) -> bool:
        user = self.get_user(user_id)
        if user:
            self.db.delete(user)
            self.db.commit()
            return True
        return False

    def list_users(self, department: str = None, skip: int = 0, limit: int = 20):
        query = self.db.query(User)
        if department:
            query = query.filter(User.department == department)
        return query.offset(skip).limit(limit).all()
