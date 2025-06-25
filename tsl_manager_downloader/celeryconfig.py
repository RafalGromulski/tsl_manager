from celery.schedules import crontab

beat_schedule = {
    "run-tsl-task-every-2-hours": {
        "task": "tasks.update_all_tsl_task",
        "schedule": crontab(minute=0, hour="*/2"),
        "options": {"queue": "tsl"},
    },
    "run-tsl-task-at-specific-hours": {
        "task": "tasks.update_all_tsl_task",
        "schedule": crontab(minute=0, hour=[9, 15]),
        "options": {"queue": "tsl"},
    },
    "run-tsl-task-daily": {
        "task": "tasks.update_all_tsl_task",
        "schedule": crontab(minute=45, hour=7),
        "options": {"queue": "tsl"},
    },
}
