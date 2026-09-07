from fastapi import FastAPI
from api.routes import router

app = FastAPI(
    title="God's Eye",
    version="0.1"
)

app.include_router(router)

@app.get("/")
def root():
    return {
        "name": "God's Eye",
        "status": "running"
    }
