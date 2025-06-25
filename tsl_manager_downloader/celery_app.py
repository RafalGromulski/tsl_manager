from celery import Celery

from celeryconfig import beat_schedule

app = Celery(
    "tsl_manager_downloader",
    broker="redis://redis:6379/0",  # Redis service with compose
    backend="redis://redis:6379/1",  # optional to log results
)

app.conf.task_routes = {
    "tasks.update_all_tsl_task": {"queue": "tsl"},
}

app.conf.beat_schedule = beat_schedule

app.conf.timezone='Europe/Warsaw'

import tasks
