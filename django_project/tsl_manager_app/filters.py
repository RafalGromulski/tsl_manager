from django_filters import AllValuesFilter, CharFilter, ChoiceFilter, FilterSet

from .choices import CrlUrlStatus, ServiceStatus, TspServiceStatus
from .models import TspServiceInfo


class MainViewFilter(FilterSet):
    """
    FilterSet used in the main view to enable filtering of TspServiceInfo records.
    Provides filters by country, provider name, service name, CRL URL status, service status,
    service type, and application handling status.
    """

    country_name = AllValuesFilter(empty_label="Country...")

    tsp_name = CharFilter(label="Service Provider...", lookup_expr="icontains")

    tsp_service_name = CharFilter(label="Service Name...", lookup_expr="icontains")

    crl_url_status_app = ChoiceFilter(
        empty_label="CRL URL Status...",
        choices=CrlUrlStatus.choices,
    )

    tsp_service_status = ChoiceFilter(
        empty_label="Service Status...",
        choices=TspServiceStatus.choices,
    )

    tsp_service_type = AllValuesFilter(
        empty_label="Service Type...",
    )

    service_status_app = ChoiceFilter(
        empty_label="Handling Status...",
        choices=ServiceStatus.choices,
    )

    class Meta:
        model = TspServiceInfo
        fields: list[str] = []
