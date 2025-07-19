from fastapi import FastAPI
from .routes import router

app = FastAPI()

@app.get("/health")
async def health():
    return {"status": "ok"}

app.include_router(router, prefix="/api")