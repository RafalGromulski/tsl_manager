import logging
import os

from celery_app import app
from main import LOGS_PATH, save_log, update_all_tsl_entries


@app.task
def update_all_tsl_task() -> None:
    """
    Celery task that downloads all TSL files and writes the update log to a CSV file.

    This task ensures the logs directory exists, runs the TSL update logic, and
    saves the output to a predefined log file path.
    """
    os.makedirs(os.path.dirname(LOGS_PATH), exist_ok=True)
    log_rows = update_all_tsl_entries()
    save_log(LOGS_PATH, log_rows)
    logging.info(f"Log saved to: {LOGS_PATH}")
