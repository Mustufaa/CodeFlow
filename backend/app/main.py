from fastapi import FastAPI

print("Loading app from:", __file__)

app = FastAPI(
    title="CodeFlow API",
    version="1.0.0",
    description="AI Powered GitHub Code Review Platform"
)


@app.get("/")
async def root():
    return {"message": "Welcome to CodeFlow API"}


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "CodeFlow API"
    }