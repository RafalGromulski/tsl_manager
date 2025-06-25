import logging
import os

from celery_app import app
from downloader import update_all_tsl_entries, LOGS_PATH, save_log


@app.task
def update_all_tsl_task():
    os.makedirs(os.path.dirname(LOGS_PATH), exist_ok=True)
    log_rows = update_all_tsl_entries()
    save_log(LOGS_PATH, log_rows)
    logging.info(f"Log saved to: {LOGS_PATH}")
