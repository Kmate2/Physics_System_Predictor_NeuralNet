from fastapi import APIRouter, Depends
from project.backend.deps import get_settings, get_artifacts

router = APIRouter()

@router.get("/health")
def health(settings = Depends(get_settings)):
    try:
        get_artifacts()  # cached; throws if broken
        return {"status": "healthy", "device": settings.device}
    except Exception as e:
        return {"status": "unhealthy", "detail": str(e), "device": settings.device}
