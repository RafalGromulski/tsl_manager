import logging

from ..choices import CrlUrlStatus, ServiceStatus
from ..models import TspServiceInfo
from .tsl_parser import ParsedService

logger = logging.getLogger(__name__)


class ServiceUpdater:
    """
    Updates or creates TSP service records based on parsed data.
    """

    def __init__(self, service_data_list: list[ParsedService]) -> None:
        """
        Initialize the updater with parsed service data.

        Args:
            service_data_list (list[ParsedService]): List of parsed TSP service entries.
        """
        self.service_data_list = service_data_list

    def run(self) -> None:
        """
        Executes the update or creation process for all provided service data.
        """
        for data in self.service_data_list:
            self._update_or_create_service(data)

    def _update_or_create_service(self, data: ParsedService) -> None:
        existing_qs = TspServiceInfo.objects.filter(
            tsp_service_name=data.tsp_service_name,
            tsp_service_digital_id=data.tsp_service_digital_id,
        )

        if existing_qs.exists():
            for obj in existing_qs:
                self._update_existing_service(obj, data)
        else:
            self._create_new_service(data)

    def _update_existing_service(self, obj: TspServiceInfo, data: ParsedService) -> None:
        updated = False

        if not obj.crl_url and data.crl_url:
            obj.crl_url = data.crl_url
            updated = True

        if obj.tsp_url != data.tsp_url:
            obj.tsp_url = data.tsp_url
            updated = True

        if obj.tsp_service_type != data.tsp_service_type:
            obj.tsp_service_type = data.tsp_service_type
            updated = True
            if obj.service_status_app != ServiceStatus.SERVED:
                if self._is_qc_ca(data):
                    obj.service_status_app = ServiceStatus.NEW_NOT_SERVED
                    obj.crl_url_status_app = CrlUrlStatus.URL_UNDEFINED
                else:
                    obj.service_status_app = ServiceStatus.WITHDRAWN_NOT_SERVED
                updated = True

        if obj.tsp_service_status != data.tsp_service_status:
            obj.tsp_service_status = data.tsp_service_status
            updated = True
            if obj.service_status_app != ServiceStatus.SERVED:
                if data.tsp_service_status == "granted":
                    obj.service_status_app = ServiceStatus.NEW_NOT_SERVED
                    obj.crl_url_status_app = CrlUrlStatus.URL_UNDEFINED
                else:
                    obj.service_status_app = ServiceStatus.WITHDRAWN_NOT_SERVED
                updated = True

        if updated:
            obj.save()
            logger.info(f"Updated service: {obj.tsp_service_name} ({obj.tsp_service_digital_id})")

    def _create_new_service(self, data: ParsedService) -> None:
        if not self._is_qc_ca(data):
            return

        kwargs: dict[str, object] = {
            "country_code": data.country_code,
            "country_name": data.country_name,
            "tsp_name": data.tsp_name,
            "tsp_service_name": data.tsp_service_name,
            "tsp_service_type": data.tsp_service_type,
            "tsp_service_status": "Granted" if data.tsp_service_status == "granted" else "Withdrawn",
            "tsp_url": data.tsp_url,
            "crl_url": data.crl_url,
            "tsp_service_digital_id": data.tsp_service_digital_id,
            "service_status_app": self._get_initial_status(data),
            "crl_url_status_app": CrlUrlStatus.URL_UNDEFINED,
        }

        if data.tsp_service_start_date is not None:
            kwargs["tsp_service_start_date"] = data.tsp_service_start_date

        new_obj = TspServiceInfo(**kwargs)
        new_obj.save()
        logger.info(f"Created new service: {new_obj.tsp_service_name} ({new_obj.tsp_service_digital_id})")

    @staticmethod
    def _is_qc_ca(data: ParsedService) -> bool:
        return data.tsp_service_type == "http://uri.etsi.org/TrstSvc/Svctype/CA/QC"

    @staticmethod
    def _get_initial_status(data: ParsedService) -> ServiceStatus:
        if data.tsp_service_status == "granted":
            return ServiceStatus.NEW_NOT_SERVED
        else:
            return ServiceStatus.WITHDRAWN_NOT_SERVED
