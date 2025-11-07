from typing import ClassVar

from django.db import models
from django.db.models.manager import Manager as DjangoManager

from .choices import CrlUrlStatus, ServiceStatus, TspServiceStatus


class TspServiceInfo(models.Model):
    objects: ClassVar[DjangoManager["TspServiceInfo"]] = models.Manager()

    country_code = models.CharField(verbose_name="Country Code", max_length=2)
    country_name = models.CharField(verbose_name="Country", max_length=20)
    tsp_name = models.CharField(verbose_name="Service Provider", max_length=255)
    tsp_service_name = models.CharField(verbose_name="Service Name", max_length=255)
    tsp_service_type = models.CharField(verbose_name="Service Type", max_length=100, default="")
    tsp_service_status = models.CharField(
        verbose_name="Service Status", max_length=50, choices=TspServiceStatus.choices
    )
    tsp_service_start_date = models.DateTimeField(verbose_name="Service Start Date")
    tsp_url = models.CharField(verbose_name="TSP URL", max_length=150, default="")
    crl_url = models.URLField(verbose_name="CRL URL", max_length=150, default="")
    tsp_service_digital_id = models.TextField(verbose_name="ID", default="")
    service_status_app = models.CharField(
        verbose_name="Handling Status",
        max_length=100,
        choices=ServiceStatus.choices,
    )
    crl_url_status_app = models.CharField(verbose_name="CRL URL Status", max_length=50, choices=CrlUrlStatus.choices)

    def __str__(self) -> str:
        return f"TSP: {self.tsp_name} — Service: {self.tsp_service_name}"


class TslValidityInfo(models.Model):
    objects: ClassVar[DjangoManager["TslValidityInfo"]] = models.Manager()

    country_code = models.CharField(verbose_name="Country Code", max_length=2)
    country_name = models.CharField(verbose_name="Country", max_length=20)
    tsl_operator_name = models.CharField(verbose_name="TSL Operator", max_length=255)
    tsl_issue_date = models.DateTimeField(verbose_name="TSL Issue Date")
    tsl_expiry_date = models.DateTimeField(verbose_name="TSL Expiry Date")
    tsl_validity_alert = models.CharField(verbose_name="TSL Status", max_length=100, default="")

    def __str__(self) -> str:
        return f"Country: {self.country_name} — TSL Operator: {self.tsl_operator_name}"
