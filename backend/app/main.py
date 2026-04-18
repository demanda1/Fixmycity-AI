from fastapi import FastAPI
from backend.app.database import init_db
from backend.app.routes import router as complaints_router

app = FastAPI(
    title="FixMyCity AI",
    description="AI-powered civic issue reporter for Indian cities",
    version="0.1.0"
)

@app.on_event("startup")
async def startup():
    init_db()
    print("Database initialized")

app.include_router(complaints_router)

@app.get("/")
async def root():
    return {"message": "FixMyCity AI is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}