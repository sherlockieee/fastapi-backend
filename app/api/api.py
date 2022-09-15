from fastapi import APIRouter

from app.api.endpoints import projects, tags

router = APIRouter()
router.include_router(projects.router)
router.include_router(tags.router)


@router.get("/")
async def root():
    return {"message": "Hello World, from FastAPI"}
