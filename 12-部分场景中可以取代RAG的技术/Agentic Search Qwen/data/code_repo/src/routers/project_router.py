"""项目路由"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from services.project_service import ProjectService
from schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse

project_router = APIRouter()

@project_router.get("/", response_model=list[ProjectResponse])
def list_projects(status: str = None, department: str = None,
                  skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    service = ProjectService(db)
    return service.list_projects(status=status, department=department,
                                skip=skip, limit=limit)

@project_router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):
    service = ProjectService(db)
    project = service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@project_router.post("/", response_model=ProjectResponse)
def create_project(data: ProjectCreate, db: Session = Depends(get_db)):
    service = ProjectService(db)
    return service.create_project(data)
