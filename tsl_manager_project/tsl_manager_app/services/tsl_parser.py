import base64
import binascii
import hashlib
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Union
from urllib.parse import urlparse
from xml.dom.minidom import parse as minidom_parse

from ..choices import ServiceStatus, CrlUrlStatus
from ..models import TspServiceInfo

logger = logging.getLogger(__name__)


class TslParser:
    def __init__(self, directory_path: Union[str, Path], countries: Dict[str, str]) -> None:
        """
        Initializes the TSL parser.

        Args:
            directory_path: Path to the directory containing XML files.
            countries: Dictionary mapping country codes to country names.
        """
        self.directory_path = str(directory_path)
        self.countries = countries

    def tsl_parse(self) -> List[Dict[str, Any]]:
        """
        Parses XML files and extracts service information.

        Returns:
            A list of dictionaries containing service data.
        """
        services = []

        for filename in os.listdir(self.directory_path):
            filepath = os.path.join(self.directory_path, filename)
            if not filepath.endswith(".xml"):
                continue

            tsl = minidom_parse(filepath)

            scheme_information = tsl.getElementsByTagNameNS("*", "SchemeInformation")[0]
            country_code = scheme_information.getElementsByTagNameNS("*", "CountryName")[0].firstChild.nodeValue
            country_name = self.countries.get(country_code, "Unknown")

            for tsp in tsl.getElementsByTagNameNS("*", "TrustServiceProvider"):
                tsp_name = self._get_text(tsp, "TSPName")
                if not tsp_name:
                    continue

                for service in tsp.getElementsByTagNameNS("*", "TSPService"):
                    service_name = self._get_text(service, "ServiceName")
                    if not service_name:
                        continue

                    service_type = self._get_text(service, "ServiceTypeIdentifier", index=0)

                    cert_value = self._get_text(service, "X509Certificate", default="")
                    service_id = ""
                    if cert_value:
                        try:
                            decoded = base64.b64decode(cert_value)
                            service_id = hashlib.sha256(decoded).hexdigest()
                        except (binascii.Error, ValueError) as e:
                            logger.warning(f"Nie można zdekodować certyfikatu: {e}")
                            service_id = ""

                    start_date_raw = self._get_text(service, "StatusStartingTime", default="")
                    try:
                        start_date = datetime.fromisoformat(start_date_raw) if start_date_raw else None
                    except ValueError as e:
                        logger.warning(f"Błędny format daty '{start_date_raw}': {e}")
                        start_date = None

                    status_uri = self._get_text(service, "ServiceStatus", default="")
                    status_simple = urlparse(status_uri).path.split("/")[-1]

                    urls = self._extract_urls(tsp, service)

                    services.append({
                        "country_code": country_code,
                        "country_name": country_name,
                        "tsp_name": tsp_name,
                        "tsp_service_name": service_name,
                        "tsp_service_type": service_type,
                        "tsp_service_status": status_simple,
                        "tsp_service_start_date": start_date,
                        "tsp_service_digital_id": service_id,
                        "tsp_url": urls["tsp_url"],
                        "crl_url": urls["crl_url"],
                    })

        return services

    @staticmethod
    def _get_text(name: Any, tag_name: str, index: int = 1, default: str = "", namespace: str = "*") -> str:
        """
        Retrieves the text content of a given XML tag.

        Args:
            name: XML element.
            tag_name: Name of the tag to retrieve.
            index: Index of the child node.
            default: Default value if tag is not found.
            namespace: XML namespace.

        Returns:
            The text content or the default value.
        """
        try:
            tag = name.getElementsByTagNameNS(namespace, tag_name)[0]
            return tag.childNodes[index].firstChild.nodeValue.strip()  # .replace("'", "")
        except (IndexError, AttributeError) as e:
            logger.debug(f"Brak tagu '{tag_name}' lub jego struktury — używam domyślnej wartości '{default}': {e}")
            return default

    @staticmethod
    def _extract_urls(tsp_node: Any, service_node: Any) -> Dict[str, str]:
        """
        Extracts TSP and CRL URLs from the XML nodes.

        Args:
            tsp_node: TrustServiceProvider XML node.
            service_node: TSPService XML node.

        Returns:
            Dictionary with 'tsp_url' and 'crl_url'.
        """
        tsp_url = ""
        crl_url = ""

        # 1. ServiceSupplyPoint
        supply_points = service_node.getElementsByTagNameNS("*", "ServiceSupplyPoint")
        if supply_points:
            url = supply_points[0].firstChild.data.strip()
            if url.endswith(".crl"):
                crl_url = url
            tsp_url = url

        # 2. TSPServiceDefinitionURI
        def_uris = service_node.getElementsByTagNameNS("*", "TSPServiceDefinitionURI")
        if def_uris and def_uris[0].childNodes:
            tsp_url = def_uris[0].childNodes[1].firstChild.data.strip()

        # 3. SchemeServiceDefinitionURI
        scheme_uris = service_node.getElementsByTagNameNS("*", "SchemeServiceDefinitionURI")
        if scheme_uris and scheme_uris[0].childNodes:
            tsp_url = scheme_uris[0].childNodes[1].firstChild.data.strip()

        # 4. ElectronicAddress
        emails = tsp_node.getElementsByTagNameNS("*", "ElectronicAddress")
        if emails:
            uris = emails[0].getElementsByTagNameNS("*", "URI")
            for uri in uris:
                if uri.getAttribute("xml:lang") == "en" and uri.firstChild.data.startswith("http"):
                    tsp_url = uri.firstChild.data.strip()

        return {"tsp_url": tsp_url, "crl_url": crl_url}


class ServiceUpdater:
    def __init__(self, service_data_list: List[Dict[str, Any]]) -> None:
        """
        Initializes the service updater.

        Args:
            service_data_list: List of dictionaries with service data.
        """
        self.service_data_list = service_data_list

    def run(self) -> None:
        """
        Executes the update or creation process for services.
        """
        for data in self.service_data_list:
            self._update_or_create_service(data)

    def _update_or_create_service(self, data: Dict[str, Any]) -> None:
        """
        Updates an existing service or creates a new one based on the provided data.

        Args:
            data: Dictionary containing service data.
        """
        existing_qs = TspServiceInfo.objects.filter(
            tsp_service_name=data["tsp_service_name"],
            tsp_service_digital_id=data["tsp_service_digital_id"],
        )

        if existing_qs.exists():
            for obj in existing_qs:
                self._update_existing_service(obj, data)
        else:
            self._create_new_service(data)

    def _update_existing_service(self, obj: TspServiceInfo, data: Dict[str, Any]) -> None:
        """
        Updates an existing TSP service object with new data if any fields have changed.

        Args:
            obj: Existing TSP service database object.
            data: New service data dictionary.
        """
        updated = False

        # URL
        if not obj.crl_url and data["crl_url"]:
            obj.crl_url = data["crl_url"]
            updated = True

        if obj.tsp_url != data["tsp_url"]:
            obj.tsp_url = data["tsp_url"]
            updated = True

        # type of service
        if obj.tsp_service_type != data["tsp_service_type"]:
            obj.tsp_service_type = data["tsp_service_type"]
            updated = True

            if obj.service_status_app != ServiceStatus.SERVED:
                if self._is_qc_ca(data):
                    obj.service_status_app = ServiceStatus.NEW_NOT_SERVED
                    obj.crl_url_status_app = CrlUrlStatus.URL_UNDEFINED
                else:
                    obj.service_status_app = ServiceStatus.WITHDRAWN_NOT_SERVED
                updated = True

        # Status ETSI (granted/withdrawn)
        if obj.tsp_service_status != data["tsp_service_status"]:
            obj.tsp_service_status = data["tsp_service_status"]
            updated = True

            if obj.service_status_app != ServiceStatus.SERVED:
                if data["tsp_service_status"] == "granted":
                    obj.service_status_app = ServiceStatus.NEW_NOT_SERVED
                    obj.crl_url_status_app = CrlUrlStatus.URL_UNDEFINED
                else:
                    obj.service_status_app = ServiceStatus.WITHDRAWN_NOT_SERVED
                updated = True

        if updated:
            obj.save()

    def _create_new_service(self, data: Dict[str, Any]) -> None:
        """
        Creates a new TSP service entry in the database if it is a QC/CA service.

        Args:
            data: Dictionary containing service data.
        """
        if not self._is_qc_ca(data):
            return  # ignore other than CA/QC

        new_obj = TspServiceInfo(
            country_code=data["country_code"],
            country_name=data["country_name"],
            tsp_name=data["tsp_name"],
            tsp_service_name=data["tsp_service_name"],
            tsp_service_type=data["tsp_service_type"],
            tsp_service_status="Granted" if data["tsp_service_status"] == "granted" else "Withdrawn",
            tsp_service_start_date=data["tsp_service_start_date"],
            tsp_url=data["tsp_url"],
            crl_url=data["crl_url"],
            tsp_service_digital_id=data["tsp_service_digital_id"],
            service_status_app=self._get_initial_status(data),
            crl_url_status_app=CrlUrlStatus.URL_UNDEFINED,
        )

        new_obj.save()

    @staticmethod
    def _is_qc_ca(data: Dict[str, Any]) -> bool:
        """
        Checks if the service type is a QC/CA service.

        Args:
            data: Service data dictionary.

        Returns:
            True if QC/CA, otherwise False.
        """
        return data["tsp_service_type"] == "http://uri.etsi.org/TrstSvc/Svctype/CA/QC"

    @staticmethod
    def _get_initial_status(data: Dict[str, Any]) -> ServiceStatus:
        """
        Determines initial application status for the service.

        Args:
            data: Service data dictionary.

        Returns:
            Corresponding ServiceStatus.
        """
        if data["tsp_service_status"] == "granted":
            return ServiceStatus.NEW_NOT_SERVED
        else:
            return ServiceStatus.WITHDRAWN_NOT_SERVED
