from fastapi import FastAPI
from backend.api.routes import router
from backend.knowledge_routes import router as knowledge_router

app = FastAPI(
    title="God's Eye",
    version="0.1",
    description="Universal Spiritual Intelligence Platform"
)

# Include routers
app.include_router(router)
app.include_router(knowledge_router)

@app.get("/")
def root():
    return {
        "name": "God's Eye",
        "status": "running",
        "version": "0.1"
    }
