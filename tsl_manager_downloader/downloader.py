import csv
import logging
import os
import xml.etree.ElementTree as ElementTree
from datetime import datetime

import certifi
import requests
import urllib3
from requests.exceptions import SSLError

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_FOLDER = os.path.join(BASE_DIR, "tsl_downloads")
LOG_DIR = os.path.join(BASE_DIR, "logs")
LOG_FILENAME = f"log_{datetime.now():%Y%m%d_%H%M%S}.csv"
LOGS_PATH = os.path.join(LOG_DIR, LOG_FILENAME)
LOTL_URL = "https://ec.europa.eu/tools/lotl/eu-lotl.xml"
NAMESPACE = {"tsl": "http://uri.etsi.org/02231/v2#"}

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def download_lotl() -> bytes:
    """
    Downloads the EU LOTL XML file content from the specified URL.

    Returns:
        Raw bytes of the LOTL XML document.
    """
    response = requests.get(LOTL_URL)
    response.raise_for_status()
    return response.content


def parse_lotl(lotl_content: bytes) -> list[tuple[str, str]]:
    """
    Parses the LOTL XML content and extracts a list of (country_code, TSL URL) tuples,
    excluding the entry for 'EU'.

    Args:
        lotl_content: Raw XML content of the LOTL file.

    Returns:
        A list of (country_code, TSL URL) tuples.
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

    Args:
        content_type: The value of the Content-Type HTTP header.

    Returns:
        True if the content type suggests XML, False otherwise.
    """
    return "xml" in content_type.lower()


def download_tsl_file(url: str, temp_path: str, verify_ssl: bool = True) -> bytes | None:
    """
    Downloads a TSL file from the given URL and saves it to a temporary path.

    Args:
        url: URL of the TSL file.
        temp_path: Temporary file path to save the downloaded content.
        verify_ssl: Whether to verify the server's SSL certificate. Use False to disable verification.

    Returns:
        The content of the downloaded file if successful, or None in case of an SSL error.
    """
    try:
        response = requests.get(url, timeout=15, verify=certifi.where() if verify_ssl else False)
        response.raise_for_status()

        with open(temp_path, "wb") as f:
            f.write(response.content)

        return response.content
    except SSLError as e:
        logging.error(f"SSL error while downloading {url}: {e}")
        return None


def download_and_replace(url: str, save_folder: str, country_code: str) -> tuple[str, bool]:
    """
    Downloads the TSL XML for a given country and replaces the existing file if valid.

    Args:
        url: TSL file URL.
        save_folder: Destination folder for saving the XML file.
        country_code: Country code for the file name.

    Returns:
        A tuple:
            - status message ("Success", "SSL Error", "Download Error", etc.)
            - boolean indicating whether the file was successfully saved.
    """
    final_path = os.path.join(save_folder, f"{country_code}.xml")
    temp_path = os.path.join(save_folder, f"{country_code}_new.xml")

    try:
        # Disable SSL verification only for problematic domain (Cyprus)
        verify_ssl = not url.startswith("https://dec.dmrid.gov.cy")
        if not verify_ssl:
            logging.warning(f"SSL verification disabled for {country_code} ({url})")

        head = requests.head(url, timeout=10, allow_redirects=True, verify=certifi.where() if verify_ssl else False)
        content_type = head.headers.get("Content-Type", "")

        if not is_valid_xml_content_type(content_type):
            logging.warning(f"Skipped {country_code}: Content-Type is {content_type}")
            return f"Skipped (Content-Type: {content_type})", False

        content = download_tsl_file(url, temp_path, verify_ssl)
        if content is None:
            return "SSL Error", False

        safely_replace_file(temp_path, final_path)
        logging.info(f"Updated {country_code}.xml")
        return "Success", True

    except requests.RequestException as e:
        logging.error(f"Download error {country_code}: {e}", exc_info=True)
        return "Download Error", False
    except OSError as e:
        logging.error(f"File error {country_code}: {e}", exc_info=True)
        return "File Error", False
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def save_log(log_path: str, rows: list[dict[str, str]]) -> None:
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


def update_all_tsl_entries() -> list[dict[str, str]]:
    """
    Parses the LOTL and attempts to download all referenced country TSL files.

    Returns:
        A list of dictionaries with log entries for each country.
    """
    os.makedirs(SAVE_FOLDER, exist_ok=True)
    lotl_content = download_lotl()
    entries = parse_lotl(lotl_content)

    log_rows = []
    logging.info("Starting TL update process...")

    for country_code, url in entries:
        status, saved = download_and_replace(url, SAVE_FOLDER, country_code)
        log_rows.append({
            "Country": country_code,
            "URL": url,
            "Status": status,
            "FileSaved": "Yes" if saved else "No"
        })

    return log_rows


def main() -> None:
    """
    Entry point: downloads and logs all country TSL files.

    Ensures the logs directory exists, processes TSL entries, and writes the log to CSV.
    """
    os.makedirs(LOG_DIR, exist_ok=True)
    log_rows = update_all_tsl_entries()
    save_log(LOGS_PATH, log_rows)
    logging.info(f"Log saved to: {LOGS_PATH}")


if __name__ == "__main__":
    main()
