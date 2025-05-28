import csv
import logging
import os
import xml.etree.ElementTree as ElementTree
from typing import List, Tuple

import requests

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_FOLDER = os.path.join(BASE_DIR, "tsl_downloads")
LOG_PATH = os.path.join(BASE_DIR, "log.csv")
LOTL_URL = "https://ec.europa.eu/tools/lotl/eu-lotl.xml"
NAMESPACE = {"tsl": "http://uri.etsi.org/02231/v2#"}

# Logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def download_lotl() -> bytes:
    """Downloads the EU LOTL XML file content from the specified URL."""
    response = requests.get(LOTL_URL)
    response.raise_for_status()
    return response.content


def parse_lotl(lotl_content: bytes) -> List[Tuple[str, str]]:
    """
    Parses the LOTL XML content and extracts a list of (country_code, TSL URL) tuples,
    excluding the entry for 'EU'.
    """
    root = ElementTree.fromstring(lotl_content)
    result = []

    for tsp in root.findall(".//tsl:OtherTSLPointer", NAMESPACE):
        url_elem = tsp.find(".//tsl:TSLLocation", NAMESPACE)
        country_code_elem = tsp.find(".//tsl:SchemeTerritory", NAMESPACE)
        if url_elem is not None and country_code_elem is not None:
            if country_code_elem.text != "EU":
                result.append((country_code_elem.text, url_elem.text))
    return result


def safely_replace_file(temp_path: str, final_path: str) -> None:
    """
    Safely replaces the final file with a temporary file.
    Removes the existing final file if it exists before renaming.
    """
    if os.path.exists(final_path):
        os.remove(final_path)
    os.rename(temp_path, final_path)


def is_valid_xml_content_type(content_type: str) -> bool:
    """
    Checks whether the provided Content-Type header indicates XML content.
    """
    return "xml" in content_type.lower()


def download_and_replace(url: str, save_folder: str, country_code: str) -> Tuple[str, bool]:
    """
    Downloads the TSL XML for a given country and replaces the existing file if valid.

    Returns:
        Tuple with status message and a boolean indicating success.
    """
    final_path = os.path.join(save_folder, f"{country_code}.xml")
    temp_path = os.path.join(save_folder, f"{country_code}_new.xml")

    try:
        # Check Content-Type
        head = requests.head(url, timeout=10, allow_redirects=True)
        content_type = head.headers.get("Content-Type", "")

        if not is_valid_xml_content_type(content_type):
            logging.warning(f"Skipped {country_code}: Content-Type is {content_type}")
            return f"Skipped (Content-Type: {content_type})", False

        # Download and save
        response = requests.get(url, timeout=15)
        response.raise_for_status()

        with open(temp_path, "wb") as f:
            f.write(response.content)

        safely_replace_file(temp_path, final_path)
        logging.info(f"Updated {country_code}.xml")
        return "Success", True

    except requests.RequestException as e:
        logging.error(f"Download error {country_code}: {e}")
    except OSError as e:
        logging.error(f"File error {country_code}: {e}")

    if os.path.exists(temp_path):
        os.remove(temp_path)
    return "Error", False


def save_log(log_path: str, rows: List[dict]) -> None:
    """
    Saves the operation log to a CSV file.

    Args:
        log_path: Path to the output log file.
        rows: List of dictionaries representing log entries.
    """
    with open(log_path, mode="w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["Country", "URL", "Status", "FileSaved"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    os.makedirs(SAVE_FOLDER, exist_ok=True)
    lotl_content = download_lotl()
    entries = parse_lotl(lotl_content)

    logging.info("Starting TL update process...")
    log_rows = []

    for country_code, url in entries:
        status, saved = download_and_replace(url, SAVE_FOLDER, country_code)
        log_rows.append({
            "Country": country_code,
            "URL": url,
            "Status": status,
            "FileSaved": "Yes" if saved else "No"
        })

    save_log(LOG_PATH, log_rows)
    logging.info(f"Log saved to: {LOG_PATH}")


if __name__ == "__main__":
    main()
