from fastapi import FastAPI
from app.api import auth
from app.api.github import router as github_router

app = FastAPI(
    title="CodeFlow API",
    version="1.0.0",
    description="AI Powered GitHub Code Review Platform"
)

app.include_router(auth.router, prefix="/api")

app.include_router(github_router)


@app.get("/")
async def root():
    return {"message": "Welcome to CodeFlow API"}


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "CodeFlow API"
    }