"""项目服务"""
from typing import Optional, List
from sqlalchemy.orm import Session
from models.project import Project
from schemas.project import ProjectCreate, ProjectUpdate

class ProjectService:
    def __init__(self, db: Session):
        self.db = db

    def get_project(self, project_id: int) -> Optional[Project]:
        return self.db.query(Project).filter(Project.id == project_id).first()

    def create_project(self, data: ProjectCreate) -> Project:
        project = Project(**data.dict())
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project

    def update_project(self, project_id: int, data: ProjectUpdate) -> Optional[Project]:
        project = self.get_project(project_id)
        if project:
            for key, value in data.dict(exclude_unset=True).items():
                setattr(project, key, value)
            self.db.commit()
            self.db.refresh(project)
        return project

    def list_projects(self, status: str = None, department: str = None,
                      skip: int = 0, limit: int = 20) -> List[Project]:
        query = self.db.query(Project)
        if status:
            query = query.filter(Project.status == status)
        if department:
            query = query.filter(Project.department == department)
        return query.offset(skip).limit(limit).all()
