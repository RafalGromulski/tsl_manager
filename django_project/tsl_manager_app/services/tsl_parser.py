import base64
import hashlib
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Mapping, Optional, TypedDict
from urllib.parse import urlparse
from xml.dom.minidom import Element, Node
from xml.dom.minidom import parse as minidom_parse

logger = logging.getLogger(__name__)


class Urls(TypedDict):
    """Return structure for `_extract_urls`."""

    tsp_url: str
    crl_url: str


@dataclass
class ParsedService:
    """
    Represents parsed data for a Trust Service Provider (TSP) service entry.
    """

    country_code: str
    country_name: str
    tsp_name: str
    tsp_service_name: str
    tsp_service_type: str
    tsp_service_status: str
    tsp_service_start_date: datetime | None
    tsp_service_digital_id: str
    tsp_url: str
    crl_url: str


class TslParser:
    """
    Parser class for extracting TSP service data from XML files in a given directory.
    """

    def __init__(self, directory_path: Path, countries: Mapping[str, str]) -> None:
        """
        Initialize the TSL parser.

        Args:
            directory_path: Path to a directory containing XML files.
            countries: Mapping of country codes to country names.
        """
        self.directory_path: Path = directory_path
        self.countries: Mapping[str, str] = countries

    def parse_all(self) -> list[ParsedService]:
        """
        Parses all XML files in the directory.

        Returns:
            list[ParsedService]: List of parsed service entries.
        """
        services: list[ParsedService] = []
        for xml_file in self.directory_path.glob("*.xml"):
            try:
                parsed_services = self._parse_file(xml_file)
                services.extend(parsed_services)
            except Exception as e:
                logger.error(f"Failed to parse {xml_file.name}: {e}")
        return services

    def _parse_file(self, path: Path) -> list[ParsedService]:
        """
        Parses a single XML file and extracts TSP service entries.

        Args:
            path (Path): Path to the XML file.

        Returns:
            list[ParsedService]: Extracted service data.
        """
        result: list[ParsedService] = []
        tsl = minidom_parse(str(path))

        scheme_info = tsl.getElementsByTagNameNS("*", "SchemeInformation")[0]
        country_code = self._get_text(scheme_info, "CountryName")
        country_name = self.countries.get(country_code, "Unknown")

        for tsp in tsl.getElementsByTagNameNS("*", "TrustServiceProvider"):
            tsp_name = self._get_text(tsp, "TSPName", index=1)
            if not tsp_name:
                continue

            for service in tsp.getElementsByTagNameNS("*", "TSPService"):
                service_name = self._get_text(service, "ServiceName", index=1)
                if not service_name:
                    continue

                service_type = self._get_text(service, "ServiceTypeIdentifier")
                if not service_type:
                    continue

                cert_value = self._get_text(service, "X509Certificate", default="")
                try:
                    digital_id = hashlib.sha256(base64.b64decode(cert_value)).hexdigest()
                except ValueError:
                    digital_id = ""

                date_str = self._get_text(service, "StatusStartingTime", default="")
                try:
                    start_date: datetime | None = datetime.fromisoformat(date_str) if date_str else None
                except ValueError:
                    start_date = None

                status_uri = self._get_text(service, "ServiceStatus", default="")
                status_simple = urlparse(status_uri).path.split("/")[-1] if status_uri else ""

                urls = self._extract_urls(tsp, service)

                result.append(
                    ParsedService(
                        country_code=country_code,
                        country_name=country_name,
                        tsp_name=tsp_name,
                        tsp_service_name=service_name,
                        tsp_service_type=service_type,
                        tsp_service_status=status_simple,
                        tsp_service_start_date=start_date,
                        tsp_service_digital_id=digital_id,
                        tsp_url=urls["tsp_url"],
                        crl_url=urls["crl_url"],
                    )
                )
        return result

    # ---------- internal helpers ----------

    @staticmethod
    def _node_text_from_first_child(node: Optional[Node]) -> Optional[str]:
        """Return stripped text of `node.firstChild.nodeValue` if present and a string."""
        if node is None:
            return None
        first = getattr(node, "firstChild", None)
        value = getattr(first, "nodeValue", None)
        return value.strip() if isinstance(value, str) else None

    @staticmethod
    def _get_text(node: Element, tag: str, index: int = 0, default: str = "") -> str:
        """
        Safely get text content from the given XML tag.

        Args:
            node: XML element to search in.
            tag: Tag local name.
            index: Index of the occurrence.
            default: Default value if the tag is missing.

        Returns:
            The text value or the default.
        """
        try:
            el = node.getElementsByTagNameNS("*", tag)[index]
        except IndexError:
            return default

        text = TslParser._node_text_from_first_child(el)
        return text if text is not None else default

    @staticmethod
    def _extract_urls(tsp_node: Element, service_node: Element) -> Urls:
        """
        Extract TSP and CRL URLs from the XML structure.

        Args:
            tsp_node: The provider node.
            service_node: The service node.

        Returns:
            A dict with keys `tsp_url` and `crl_url`.
        """
        tsp_url = ""
        crl_url = ""

        supply_points = service_node.getElementsByTagNameNS("*", "ServiceSupplyPoint")
        if supply_points:
            text = TslParser._node_text_from_first_child(supply_points[0])
            if isinstance(text, str):
                if text.endswith(".crl"):
                    crl_url = text
                tsp_url = text

        def_uris = service_node.getElementsByTagNameNS("*", "TSPServiceDefinitionURI")
        if def_uris and def_uris[0].childNodes and len(def_uris[0].childNodes) > 1:
            candidate = getattr(def_uris[0].childNodes[1], "firstChild", None)
            value = getattr(candidate, "nodeValue", None)
            if isinstance(value, str) and value.strip():
                tsp_url = value.strip()

        scheme_uris = service_node.getElementsByTagNameNS("*", "SchemeServiceDefinitionURI")
        if scheme_uris and scheme_uris[0].childNodes and len(scheme_uris[0].childNodes) > 1:
            candidate = getattr(scheme_uris[0].childNodes[1], "firstChild", None)
            value = getattr(candidate, "nodeValue", None)
            if isinstance(value, str) and value.strip():
                tsp_url = value.strip()

        emails = tsp_node.getElementsByTagNameNS("*", "ElectronicAddress")
        if emails:
            uris = emails[0].getElementsByTagNameNS("*", "URI")
            for uri in uris:
                if uri.getAttribute("xml:lang") == "en":
                    value = TslParser._node_text_from_first_child(uri)
                    if isinstance(value, str) and value:
                        tsp_url = value
                        break

        return {"tsp_url": tsp_url, "crl_url": crl_url}
