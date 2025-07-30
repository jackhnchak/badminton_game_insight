from fastapi import APIRouter, UploadFile, File
import os
from worker.worker import process_video_task

router = APIRouter()

@router.post("/upload")
async def upload_video(video: UploadFile = File(...)):
    # Ensure upload directory exists
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)

    # Save uploaded file
    upload_path = os.path.join(upload_dir, video.filename)
    contents = await video.read()
    with open(upload_path, "wb") as f:
        f.write(contents)

    # Dispatch processing to Celery
    task = process_video_task.delay(upload_path, "output")

    return {
        "message": "Processing started",
        "task_id": task.id
    }

@router.get("/status/{task_id}")
async def get_status(task_id: str):
    """Return Celery task state and CSV path when done."""
    res = process_video_task.AsyncResult(task_id)
    return {
        "state": res.state,
        "result": res.result if res.ready() else None
    }