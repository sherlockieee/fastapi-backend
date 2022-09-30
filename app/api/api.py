from fastapi import APIRouter

from app.api.endpoints import projects, tags, user

router = APIRouter()
router.include_router(projects.router)
router.include_router(tags.router)
router.include_router(user.router)


@router.get("/")
async def root():
    return {"message": "Hello World, from FastAPI"}
