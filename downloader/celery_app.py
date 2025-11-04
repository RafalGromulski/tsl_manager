# Import tasks to ensure Celery auto-discovers them
from celery import Celery

from downloader import tasks  # noqa: F401
from downloader.celeryconfig import beat_schedule

app = Celery(
    "main",
    broker="redis://redis:6379/0",  # Redis service with docker-compose
    backend="redis://redis:6379/1",  # For task results (optional)
)

# Configure routing for specific tasks to a dedicated queue
app.conf.task_routes = {
    "tasks.update_all_tsl_task": {"queue": "tsl"},
}

# Configure periodic task schedules
app.conf.beat_schedule = beat_schedule
app.conf.timezone = "Europe/Warsaw"
app.conf.enable_utc = False
