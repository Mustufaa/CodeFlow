from fastapi import FastAPI
from app.api import auth
from app.api.github import router as github_router
from app.api.tenant import router as tenant_router
from app.api.github_installation import router as github_installation_router
from app.api.repository import router as repository_router

app = FastAPI(
    title="CodeFlow API",
    version="1.0.0",
    description="AI Powered GitHub Code Review Platform"
)

app.include_router(auth.router, prefix="/api")

app.include_router(github_router)
app.include_router(tenant_router)
app.include_router(github_installation_router)
app.include_router(repository_router)

@app.get("/")
async def root():
    return {"message": "Welcome to CodeFlow API"}


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "CodeFlow API"
    }