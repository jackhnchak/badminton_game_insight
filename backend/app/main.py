from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .routes import router

app = FastAPI()

origins = [
    "http://localhost:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve processed CSVs
app.mount("/output", StaticFiles(directory="output"), name="output")

@app.get("/health")
async def health():
    return {"status": "ok"}

app.include_router(router, prefix="/api")