from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from routes import router
from core import settings
from starlette.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI(
    title="Reminder API",
    description="API for reminder service with voice call capability",
    version="1.0.0"
)

# Middleware для проверки доступа к странице документации с базовой авторизацией
security = HTTPBasic(auto_error=False)

from starlette.middleware.base import BaseHTTPMiddleware

class DocsAccessMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path in ["/docs", "/redoc"]:
            credentials: HTTPBasicCredentials = await security(request)
            if not (credentials and credentials.username == "admin" and credentials.password == "cockandballstorture"):
                # Return a 401 response with WWW-Authenticate header so the browser shows a login prompt.
                return Response(
                    content="Unauthorized",
                    status_code=401,
                    headers={"WWW-Authenticate": 'Basic realm="Docs"'}
                )
        response = await call_next(request)
        return response

app.add_middleware(DocsAccessMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # TODO: change to configs.ALLOWED_HOSTS
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files so that audio files can be served
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(router)

# Simple health check route
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {"status": "healthy"}

# # Define startup event to create necessary directories
# @app.on_event("startup")
# async def startup_event():
#     os.makedirs("/shared_audio/audio", exist_ok=True)
    
# If the file is run directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)