from typing import List
from fastapi import APIRouter, status, HTTPException


from app.prisma.prisma import db
import app.schemas.project as schema


router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("/", response_model=List[schema.ProjectOut])
async def get_projects(offset: int = 0, limit: int = 100):
    all_projects = await db.project.find_many(
        skip=offset, take=limit, include={"tags": True}
    )
    return all_projects


@router.get("/{project_id}", response_model=schema.ProjectOut)
async def get_one_project(project_id: int):
    project = await db.project.find_unique(
        where={"id": project_id}, include={"tags": True}
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schema.ProjectOut)
async def create_project(project: schema.ProjectIn):
    new_project = await db.project.create(
        data={
            **project.dict(),
            "tags": {"create": list(map(lambda x: {"name": x.name}, project.tags))},
        }
    )

    # refresh
    new_project = await db.project.find_unique(
        where={"id": new_project.id}, include={"tags": True}
    )

    return new_project


@router.post(
    "/{project_id}/tags/{tag_id}",
    status_code=status.HTTP_201_CREATED,
    response_model=schema.ProjectOut,
)
async def add_tag_to_project(
    project_id: int,
    tag_id: int,
):
    project = await db.project.find_unique(
        where={"id": project_id}, include={"tags": True}
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    tag = await db.tag.find_unique(where={"id": tag_id})
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    if tag in project.tags:
        raise HTTPException(status_code=403, detail="Tag already in Project")

    tag_id_list = list(map(lambda x: {"id": x.id}, project.tags))
    tag_id_list.append({"id": tag.id})
    await db.project.update(
        where={"id": project_id}, data={**project.dict(), "tags": {"set": tag_id_list}}
    )

    # refresh
    project = await db.project.find_unique(
        where={
            "id": project_id,
        },
        include={"tags": True},
    )

    return project
