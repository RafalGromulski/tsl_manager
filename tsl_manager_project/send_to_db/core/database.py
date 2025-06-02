import asyncpg
import logging
from typing import List

from send_to_db.config.config import load_config
from send_to_db.core.parser import TSPService

logger = logging.getLogger(__name__)


async def insert_services_to_db(services: List[TSPService]) -> None:
    params = load_config()
    conn = await asyncpg.connect(**params)

    sql = """
    INSERT INTO tsl_manager_app_tspserviceinfo (
        country_code, country_name, tsp_name, tsp_service_name,
        tsp_service_type, tsp_service_status, tsp_service_start_date,
        tsp_url, crl_url, tsp_service_digital_id, service_status_app, crl_url_status_app
    ) VALUES (
        $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12
    )
    """

    try:
        async with conn.transaction():
            for s in services:
                await conn.execute(sql,
                                   s.country_code, s.country_name, s.tsp_name, s.service_name,
                                   s.service_type, s.service_status, s.service_start_date,
                                   s.tsp_url, s.crl_url, s.service_digital_id,
                                   s.service_status_app, s.crl_url_status_app
                                   )
        logger.info(f"Inserted {len(services)} services into the database.")
    except Exception as e:
        logger.error(f"Database error: {e}")
    finally:
        await conn.close()
