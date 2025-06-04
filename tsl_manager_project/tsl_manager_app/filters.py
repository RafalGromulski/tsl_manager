from django_filters import AllValuesFilter, CharFilter, ChoiceFilter, FilterSet

from .choices import TspServiceStatus, ServiceStatus, CrlUrlStatus
from .models import TspServiceInfo


class MainViewFilter(FilterSet):
    """
    FilterSet used in the main view to enable filtering of TspServiceInfo records.
    Provides filters by country, provider name, service name, CRL URL status, service status,
    service type, and application handling status.
    """
    country_name = AllValuesFilter(empty_label="Państwo...")

    tsp_name = CharFilter(label="Dostawca usługi...", lookup_expr="icontains")

    tsp_service_name = CharFilter(label="Nazwa usługi...", lookup_expr="icontains")

    crl_url_status_app = ChoiceFilter(
        empty_label="Status CRL URL...",
        choices=CrlUrlStatus.choices,
    )

    tsp_service_status = ChoiceFilter(
        empty_label="Status usługi...",
        choices=TspServiceStatus.choices,
    )

    tsp_service_type = AllValuesFilter(
        empty_label="Typ usługi...",
    )

    service_status_app = ChoiceFilter(
        empty_label="Status obsługi usługi...",
        choices=ServiceStatus.choices,
    )

    class Meta:
        model = TspServiceInfo
        fields = []
