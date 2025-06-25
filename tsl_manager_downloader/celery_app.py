from celery import Celery

from celeryconfig import beat_schedule

app = Celery(
    "tsl_manager_downloader",
    broker="redis://redis:6379/0",  # Redis service with docker-compose
    backend="redis://redis:6379/1",  # For task results (optional)
)

# Configure routing for specific tasks to a dedicated queue
app.conf.task_routes = {
    "tasks.update_all_tsl_task": {"queue": "tsl"},
}

# Configure periodic task schedules
app.conf.beat_schedule = beat_schedule
app.conf.timezone = 'Europe/Warsaw'

# Import tasks to ensure Celery auto-discovers them
import tasks  # noqa: F401
