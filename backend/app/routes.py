from fastapi import APIRouter, UploadFile, File
from worker.worker import process_video_task  # Celery task

router = APIRouter()

@router.post("/upload")
async def upload_video(video: UploadFile = File(...)):
    # 1. Save the uploaded file
    upload_path = f"uploads/{video.filename}"
    contents = await video.read()
    with open(upload_path, "wb") as f:
        f.write(contents)

    # 2. Dispatch to Celery
    task = process_video_task.delay(upload_path, "output")

    # 3. Return the Celery task ID to the client
    return {
        "message": "Processing started",
        "task_id": task.id
    }