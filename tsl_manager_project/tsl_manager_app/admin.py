from django.contrib import admin

from .models import TspServiceInfo, TslValidityInfo


@admin.register(TspServiceInfo)
class TSPAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "country_code",
        "country_name",
        "tsp_name",
        "tsp_service_name",
        "tsp_service_type",
        "tsp_service_status",
        "tsp_service_start_date",
        "tsp_url",
        "crl_url",
        "tsp_service_digital_id",
        "service_status_app",
        "crl_url_status_app",
    ]
    list_filter = ["country_name"]
    search_fields = [
        "country_name",
        "tsp_name",
    ]


admin.site.register(TslValidityInfo)
