from typing import List
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import insert


import app.models as models
from app.api.deps import get_current_active_user, get_db
import app.schemas.project as schema
from app.schemas.project_status import ProjectStatus
from app.models import project_tags
from app.utils.backers import get_total_credits_bought

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("/", response_model=List[schema.ProjectOut])
def get_projects(
    db: Session = Depends(get_db),
    offset: int = 0,
    limit: int = 100,
):
    all_projects = (
        db.query(models.Project)
        .filter(models.Project.status == ProjectStatus.IN_FUNDING)
        .options(
            joinedload(models.Project.backers).options(
                joinedload(models.BackerProjectOrder.backer)
            )
        )
        .offset(offset)
        .limit(limit)
        .all()
    )
    return all_projects


@router.get("/me/backer", response_model=List[schema.ProjectInBackerSummary])
def get_all_projects_backed_by_current_user(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    all_projects = (
        db.query(models.Project)
        .options(
            joinedload(models.Project.backers).options(
                joinedload(models.BackerProjectOrder.backer)
            )
        )
        .filter(models.Project.backers.any(models.User.id == current_user.id))
        .all()
    )

    print(jsonable_encoder(all_projects[0]))

    for proj in all_projects:
        proj.total_credits_bought = get_total_credits_bought(proj.backers, current_user)
    return all_projects


@router.get("/me/owner", response_model=List[schema.ProjectOut])
def get_all_projects_owned_by_current_user(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    all_projects = (
        db.query(models.Project)
        .filter(models.Project.owner_id == current_user.id)
        .all()
    )
    return all_projects


@router.get("/{project_id}", response_model=schema.ProjectOut)
def get_one_project(project_id: int, db: Session = Depends(get_db)):
    project = (
        db.query(models.Project)
        .options(
            joinedload(models.Project.backers).options(
                joinedload(models.BackerProjectOrder.backer)
            )
        )
        .filter(models.Project.id == project_id)
        .first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schema.ProjectOut)
def create_project(
    project: schema.ProjectIn,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    project_dict = jsonable_encoder(project)
    # project_tags = project_dict["tags"]
    # project_dict["tags"] = []
    new_project = models.Project(**project_dict, owner_id=current_user.id)
    db.add(new_project)

    # update project owner status
    db.commit()
    db.refresh(new_project)

    # for tag in project_tags:
    #     existing = db.query(models.Tag).filter(models.Tag.id == tag["id"]).first()
    #     if existing:
    #         new_project.tags.append(existing)
    #     if not existing:
    #         new_tag = models.Tag(name=tag["name"])
    #         new_project.tags.append(new_tag)
    #         db.add(new_tag)

    # db.commit()
    # db.refresh(new_project)

    return new_project


@router.post(
    "/{project_id}/tags/{tag_id}",
    status_code=status.HTTP_201_CREATED,
    response_model=schema.ProjectOut,
)
def add_tag_to_project(project_id: int, tag_id: int, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    tag = db.query(models.Tag).filter(models.Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    if tag in project.tags:
        raise HTTPException(status_code=403, detail="Tag already in project")

    db.execute(insert(project_tags).values(project_id=project_id, tag_id=tag_id))
    db.commit()
    db.refresh(project)
    return project


@router.delete(
    "/{project_id}/tags/{tag_id}",
    status_code=status.HTTP_200_OK,
    response_model=schema.ProjectOut,
)
def delete_tag_from_project(
    project_id: int, tag_id: int, db: Session = Depends(get_db)
):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    tag = db.query(models.Tag).filter(models.Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    if tag not in project.tags:
        raise HTTPException(status_code=403, detail="Tag is not in project")

    project.tags.remove(tag)
    db.commit()
    db.refresh(project)
    return project
