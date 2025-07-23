import binascii
import logging
import xml.dom.minidom as minidom
from base64 import b64decode
from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
from pathlib import Path
from urllib.parse import urlparse

from send_to_db.core.constants import COUNTRIES_EN, CA_QC_URI

logger = logging.getLogger(__name__)


@dataclass
class TSPService:
    """
    Data class representing a Trust Service Provider (TSP) service entry.
    """
    country_code: str
    country_name: str
    tsp_name: str
    service_name: str
    service_type: str
    service_status: str
    service_start_date: datetime
    tsp_url: str
    crl_url: str
    service_digital_id: str
    service_status_app: str
    crl_url_status_app: str


class TSPServiceParser:
    """
    A parser class responsible for extracting TSPService information from XML files in a given directory.
    """

    def __init__(self, directory: Path):
        """
        Initialize the parser with the given directory containing XML files.

        Args:
            directory (Path): Path to the directory with XML files.
        """
        self.directory = directory

    def parse_all(self) -> list[TSPService]:
        """
        Parse all XML files in the specified directory.

        Returns:
            list[TSPService]: A list of parsed TSPService entries.
        """
        all_services = []
        for file_path in self.directory.glob("*.xml"):
            try:
                services = self._parse_file(file_path)
                all_services.extend(services)
            except Exception as e:
                logger.error(f"Failed to parse {file_path.name}: {e}")
        return all_services

    def _parse_file(self, path: Path) -> list[TSPService]:
        """
        Parse a single XML file and extract valid TSP services.

        Args:
            path (Path): Path to the XML file.

        Returns:
            list[TSPService]: A list of TSPService entries found in the file.
        """
        result = []
        doc = minidom.parse(str(path))

        for tsp in doc.getElementsByTagNameNS("*", "TrustServiceProvider"):
            for service in tsp.getElementsByTagNameNS("*", "TSPService"):
                try:
                    service_type = self._get_text(service, "ServiceTypeIdentifier", default="")
                    if service_type != CA_QC_URI:
                        continue

                    service_status_uri = self._get_text(service, "ServiceStatus", default="")
                    if urlparse(service_status_uri).path.split("/")[-1] != "granted":
                        continue

                    scheme = doc.getElementsByTagNameNS("*", "SchemeInformation")[0]
                    country_code = self._get_text(scheme, "CountryName")
                    country_name = COUNTRIES_EN.get(country_code, "Unknown")

                    tsp_name = tsp.getElementsByTagNameNS("*", "TSPName")[0].childNodes[1].firstChild.nodeValue.replace("'", "")
                    service_name = service.getElementsByTagNameNS("*", "ServiceName")[0].childNodes[1].firstChild.nodeValue.replace("'", "")
                    # start_date = datetime.fromisoformat(service.getElementsByTagNameNS("*", "StatusStartingTime")[0].firstChild.nodeValue)

                    start_date_str = self._get_text(service, "StatusStartingTime", default="")
                    try:
                        start_date = datetime.fromisoformat(start_date_str)
                    except ValueError as e:
                        logger.warning(f"Invalid date format in {path.name}: {e}")
                        # start_date = datetime.fromisoformat("1970-01-01T00:00:00")
                        continue

                    cert = self._get_text(service, "X509Certificate")
                    try:
                        digital_id = sha256(b64decode(cert)).hexdigest()
                    except (binascii.Error, ValueError) as e:
                        logger.warning(f"Invalid certificate format in {path.name}: {e}")
                        digital_id = ""

                    tsp_url, crl_url = self._extract_urls(tsp, service)
                    result.append(TSPService(
                        country_code=country_code,
                        country_name=country_name,
                        tsp_name=tsp_name,
                        service_name=service_name,
                        service_type=service_type,
                        service_status="Granted",
                        service_start_date=start_date,
                        tsp_url=tsp_url,
                        crl_url=crl_url,
                        service_digital_id=digital_id,
                        service_status_app="Not served (new)",
                        crl_url_status_app="CRL URL undefined"
                    ))
                except Exception as e:
                    logger.warning(f"Error parsing service in {path.name}: {e}")
        return result

    @staticmethod
    def _get_text(element: minidom.Element, tag_name: str, index: int = 0, default: str = "", namespace: str = "*") -> str:
        """
        Helper to extract text from an XML tag, safely.

        Args:
            element: XML element to search in.
            tag_name: Name of the tag.
            index: Index of the tag occurrence.
            default: Default value if not found.
            namespace: XML namespace (default '*').

        Returns:
            Text content or default.
        """
        try:
            tag = element.getElementsByTagNameNS(namespace, tag_name)[index]
            return tag.firstChild.nodeValue.strip()
        except (IndexError, AttributeError):
            logger.debug(f"Missing tag '{tag_name}' or structure in XML. Returning default: '{default}'")
            return default

    @staticmethod
    def _extract_urls(tsp: minidom.Element, service: minidom.Element) -> tuple[str, str]:
        """
        Extract TSP and CRL URLs from the given XML elements.

        Args:
            tsp: The TrustServiceProvider XML node.
            service: The TSPService XML node.

        Returns:
            tuple[str, str]: A tuple containing the TSP URL and CRL URL.
        """
        tsp_url = ""
        crl_url = ""

        supply = service.getElementsByTagNameNS("*", "ServiceSupplyPoint")
        if supply and supply[0].firstChild:
            tsp_url = supply[0].firstChild.nodeValue
            if tsp_url.endswith(".crl"):
                crl_url = tsp_url

        def_uri = service.getElementsByTagNameNS("*", "TSPServiceDefinitionURI")
        scheme_uri = service.getElementsByTagNameNS("*", "SchemeServiceDefinitionURI")

        if def_uri:
            tsp_url = def_uri[0].childNodes[1].firstChild.nodeValue
        elif scheme_uri:
            tsp_url = scheme_uri[0].childNodes[1].firstChild.nodeValue
        else:
            address = tsp.getElementsByTagNameNS("*", "ElectronicAddress")
            if address:
                for uri in address[0].getElementsByTagNameNS("*", "URI"):
                    if uri.getAttribute("xml:lang") == "en":
                        tsp_url = uri.firstChild.nodeValue
                        break

        return tsp_url, crl_url
