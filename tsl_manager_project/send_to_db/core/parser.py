import logging
import xml.dom.minidom as minidom
from base64 import b64decode
from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
from pathlib import Path
from typing import List
from urllib.parse import urlparse

from send_to_db.core.constants import COUNTRIES_EN

logger = logging.getLogger(__name__)


@dataclass
class TSPService:
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
    def __init__(self, directory: Path):
        self.directory = directory

    def parse_all(self) -> List[TSPService]:
        all_services = []
        for file_path in self.directory.glob("*.xml"):
            try:
                services = self._parse_file(file_path)
                all_services.extend(services)
            except Exception as e:
                logger.error(f"Failed to parse {file_path.name}: {e}")
        return all_services

    def _parse_file(self, path: Path) -> List[TSPService]:
        result = []
        doc = minidom.parse(str(path))

        for tsp in doc.getElementsByTagNameNS("*", "TrustServiceProvider"):
            for service in tsp.getElementsByTagNameNS("*", "TSPService"):
                try:
                    service_type = service.getElementsByTagNameNS("*", "ServiceTypeIdentifier")[0].firstChild.nodeValue
                    if service_type != "http://uri.etsi.org/TrstSvc/Svctype/CA/QC":
                        continue

                    service_status_uri = service.getElementsByTagNameNS("*", "ServiceStatus")[0].firstChild.nodeValue
                    if urlparse(service_status_uri).path.split("/")[-1] != "granted":
                        continue

                    scheme = doc.getElementsByTagNameNS("*", "SchemeInformation")[0]
                    country_code = scheme.getElementsByTagNameNS("*", "CountryName")[0].firstChild.nodeValue
                    country_name = COUNTRIES_EN.get(country_code, "Unknown")

                    tsp_name = tsp.getElementsByTagNameNS("*", "TSPName")[0].childNodes[1].firstChild.nodeValue.replace("'", "")
                    service_name = service.getElementsByTagNameNS("*", "ServiceName")[0].childNodes[1].firstChild.nodeValue.replace("'", "")
                    start_date = datetime.fromisoformat(service.getElementsByTagNameNS("*", "StatusStartingTime")[0].firstChild.nodeValue)

                    digital_id = ""
                    try:
                        cert = service.getElementsByTagNameNS("*", "X509Certificate")[0].firstChild.nodeValue
                        digital_id = sha256(b64decode(cert)).hexdigest()
                    except Exception:
                        pass

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
                        crl_url_status_app="CRL URL undetermined"
                    ))
                except Exception as e:
                    logger.warning(f"Error parsing service in {path.name}: {e}")
        return result

    def _extract_urls(self, tsp, service):
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
