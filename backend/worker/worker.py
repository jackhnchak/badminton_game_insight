from celery import Celery
from app.processor import process_video  # your real processing fn

# 1) Create & export a Celery app named “celery”
celery = Celery(
    'badminton',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0',
)

# (Optional) tweak serializers / timezone
celery.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

# 2) Wrap your process_video call in a task
@celery.task(name='process_video_task')
def process_video_task(input_path: str, output_folder: str) -> str:
    # Calls your existing processor.process_video(...)
    return process_video(input_path, output_folder)