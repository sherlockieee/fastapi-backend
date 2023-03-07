from typing import List
from fastapi import APIRouter, Depends, status, HTTPException, Query, BackgroundTasks
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import insert

import app.models as models
from app.api.deps import get_current_active_user, get_db
import app.schemas.project as schema
from app.schemas.project_status import ProjectStatus
from app.models import project_tags
from app.utils.backers import get_total_credits_bought
from app.utils.emails import (
    send_email_when_funding_reaches,
    send_email_when_project_fails,
)
from app.api.endpoints.refunds import refund_project

router = APIRouter(prefix="/projects", tags=["projects"])


def update_status(background_tasks, db):
    finished_projects: List[schema.Project] = (
        db.query(models.Project)
        .filter(models.Project.status.in_([ProjectStatus.IN_FUNDING]))
        .filter(models.Project.days_remaining <= 0)
        .options(
            joinedload(models.Project.users).options(
                joinedload(models.Transaction.user)
            )
        )
        .all()
    )
    for project in finished_projects:
        print(project.id, project.percentage_raised)
        if project.percentage_raised < 100:
            project.status = ProjectStatus.FAIL

            send_email_when_project_fails(
                background_tasks=background_tasks, project=project
            )
            refund_project(background_tasks, project_id=project.id, db=db)

        else:
            project.status = ProjectStatus.SUCCESS
            send_email_when_funding_reaches(background_tasks, project)
        db.commit()


@router.get("/", response_model=List[schema.ProjectOut])
async def get_projects(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    offset: int = 0,
    limit: int = 100,
    filtered_status: List[ProjectStatus] = Query(default=[ProjectStatus.IN_FUNDING]),
    order_by: List[str] = Query(default=None),
):
    update_status(background_tasks, db)
    query = (
        db.query(models.Project)
        .filter(models.Project.status.in_(filtered_status))
        .options(
            joinedload(models.Project.users).options(
                joinedload(models.Transaction.user)
            )
        )
    )
    if order_by:
        for col in order_by:
            if col not in schema.Project.__fields__.keys():
                pass
            query = query.order_by(getattr(models.Project, col))
    all_projects = query.offset(offset).limit(limit).all()
    return all_projects


@router.get("/me/backer", response_model=List[schema.ProjectOut])
def get_all_projects_backed_by_current_user(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    all_projects = (
        db.query(models.Project)
        .join(models.Transaction)
        .join(models.User)
        .options(
            joinedload(models.Project.users).options(
                joinedload(models.Transaction.user)
            )
        )
        .filter(models.Project.users.any(models.User.id == current_user.id))
        .all()
    )

    for proj in all_projects:
        proj.total_credits_bought = get_total_credits_bought(proj.users, current_user)
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
            joinedload(models.Project.users).options(
                joinedload(models.Transaction.user)
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
