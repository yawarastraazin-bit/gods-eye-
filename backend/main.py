from fastapi import FastAPI

app = FastAPI(
    title="God's Eye",
    version="0.1"
)

@app.get("/")
def root():
    return {
        "name": "God's Eye",
        "status": "running"
    }
