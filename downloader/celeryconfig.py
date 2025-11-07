from typing import Any

from celery.schedules import crontab

# Celery beat schedule — defines periodic execution times for tasks.
# Keys are schedule names, values are dicts with:
#   - "task": import path to the task function
#   - "schedule": crontab or timedelta defining execution time
#   - "options": Celery task options like the queue name

beat_schedule: dict[str, dict[str, Any]] = {
    "run-tsl-task-every-2-hours": {
        "task": "tasks.update_all_tsl_task",
        "schedule": crontab(minute=0, hour="*/2"),
        "options": {"queue": "tsl"},
    },
}
