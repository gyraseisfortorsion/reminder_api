from fastapi import APIRouter
from .auth import router as auth_router
from .reminders import router as reminders_router
from .communications import router as communications_router
from .llm import router as llm_router
from .messages import router as messages_router
router = APIRouter(prefix="/v1")

router.include_router(auth_router)
router.include_router(reminders_router)
router.include_router(communications_router)
router.include_router(llm_router)
router.include_router(messages_router)