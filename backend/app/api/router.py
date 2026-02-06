from fastapi import APIRouter
from .process import router as process_router
from .agents import router as agents_router
from .documents import router as documents_router
from .chat import router as chat_router
from .meeting import router as meeting_router
from .report import router as report_router

router = APIRouter()
router.include_router(process_router, prefix="/api")
router.include_router(agents_router, prefix="/api")
router.include_router(documents_router, prefix="/api")
router.include_router(chat_router, prefix="/api")
router.include_router(meeting_router, prefix="/api")
router.include_router(report_router, prefix="/api")
