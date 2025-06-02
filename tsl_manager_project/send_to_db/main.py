import asyncio
import logging
from pathlib import Path

from core.database import insert_services_to_db
from core.parser import TSPServiceParser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIRECTORY = BASE_DIR / "data" / "data1"


async def main():
    logger.info("Loading and parsing TSP XML data...")

    parser = TSPServiceParser(DATA_DIRECTORY)
    services = parser.parse_all()

    logger.info(f"Parsed {len(services)} services. Inserting into database...")
    await insert_services_to_db(services)

    logger.info("Done.")


if __name__ == "__main__":
    asyncio.run(main())
