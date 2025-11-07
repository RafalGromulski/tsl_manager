import logging
import xml.dom.minidom as minidom
from base64 import b64decode
from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

from .constants import CA_QC_URI, COUNTRIES_EN

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
        all_services: list[TSPService] = []
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
        result: list[TSPService] = []
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

                    tsp_name_raw = self._child_index_text(tsp.getElementsByTagNameNS("*", "TSPName"), 0, child_index=1)
                    tsp_name = tsp_name_raw.replace("'", "") if tsp_name_raw else ""

                    service_name_raw = self._child_index_text(
                        service.getElementsByTagNameNS("*", "ServiceName"), 0, child_index=1
                    )
                    service_name = service_name_raw.replace("'", "") if service_name_raw else ""

                    start_date_str = self._get_text(service, "StatusStartingTime", default="")
                    try:
                        start_date = datetime.fromisoformat(start_date_str)
                    except ValueError as e:
                        logger.warning(f"Invalid date format in {path.name}: {e}")
                        continue

                    cert = self._get_text(service, "X509Certificate", default="")
                    try:
                        service_digital_id = sha256(b64decode(cert, validate=True)).hexdigest()
                    except ValueError as e:
                        logger.warning(f"Invalid certificate format in {path.name}: {e}")
                        service_digital_id = ""

                    tsp_url, crl_url = self._extract_urls(tsp, service)

                    result.append(
                        TSPService(
                            country_code=country_code,
                            country_name=country_name,
                            tsp_name=tsp_name,
                            service_name=service_name,
                            service_type=service_type,
                            service_status="Granted",
                            service_start_date=start_date,
                            tsp_url=tsp_url,
                            crl_url=crl_url,
                            service_digital_id=service_digital_id,
                            service_status_app="Not served (new)",
                            crl_url_status_app="CRL URL undefined",
                        )
                    )
                except Exception as e:
                    logger.warning(f"Error parsing service in {path.name}: {e}")
        return result

    # ----------------------- helpers (mypy-safe) -----------------------
    @staticmethod
    def _first_child_text(node: Optional[minidom.Node]) -> Optional[str]:
        """
        Return stripped text of node.firstChild.nodeValue if present and a string.
        """
        if node is None:
            return None
        first = getattr(node, "firstChild", None)
        value = getattr(first, "nodeValue", None)
        return value.strip() if isinstance(value, str) else None

    @staticmethod
    def _get_text(
        element: minidom.Element,
        tag_name: str,
        index: int = 0,
        default: str = "",
        namespace: str = "*",
    ) -> str:
        """
        Helper to extract text from an XML tag, safely.
        """
        try:
            tag = element.getElementsByTagNameNS(namespace, tag_name)[index]
        except IndexError:
            logger.debug(f"Missing tag '{tag_name}' at index {index}. Returning default '{default}'.")
            return default

        text = TSPServiceParser._first_child_text(tag)
        return text if text is not None else default

    @staticmethod
    def _child_index_text(elements: list[minidom.Element], index: int, *, child_index: int) -> Optional[str]:
        """
        For nodes that have localized text at childNodes[child_index].firstChild.nodeValue,
        return the stripped text safely or None.
        """
        try:
            el = elements[index]
        except IndexError:
            return None
        children = getattr(el, "childNodes", None)
        if not children or len(children) <= child_index:
            return None
        candidate = getattr(children[child_index], "firstChild", None)
        value = getattr(candidate, "nodeValue", None)
        return value.strip() if isinstance(value, str) else None

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

        # ServiceSupplyPoint
        supply = service.getElementsByTagNameNS("*", "ServiceSupplyPoint")
        if supply:
            text = TSPServiceParser._first_child_text(supply[0])
            if isinstance(text, str):
                if text.endswith(".crl"):
                    crl_url = text
                tsp_url = text

        # TSPServiceDefinitionURI / SchemeServiceDefinitionURI
        def_uri = service.getElementsByTagNameNS("*", "TSPServiceDefinitionURI")
        scheme_uri = service.getElementsByTagNameNS("*", "SchemeServiceDefinitionURI")

        if def_uri and getattr(def_uri[0], "childNodes", None) and len(def_uri[0].childNodes) > 1:
            candidate = getattr(def_uri[0].childNodes[1], "firstChild", None)
            value = getattr(candidate, "nodeValue", None)
            if isinstance(value, str) and value.strip():
                tsp_url = value.strip()
        elif scheme_uri and getattr(scheme_uri[0], "childNodes", None) and len(scheme_uri[0].childNodes) > 1:
            candidate = getattr(scheme_uri[0].childNodes[1], "firstChild", None)
            value = getattr(candidate, "nodeValue", None)
            if isinstance(value, str) and value.strip():
                tsp_url = value.strip()
        else:
            address = tsp.getElementsByTagNameNS("*", "ElectronicAddress")
            if address:
                for uri in address[0].getElementsByTagNameNS("*", "URI"):
                    if uri.getAttribute("xml:lang") == "en":
                        maybe_text = TSPServiceParser._first_child_text(uri)
                        if isinstance(maybe_text, str) and maybe_text:
                            tsp_url = maybe_text
                            break

        return tsp_url, crl_url
