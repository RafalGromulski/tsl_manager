from django.db import models

from .choices import TspServiceStatus, ServiceStatus, CrlUrlStatus

class TspServiceInfo(models.Model):
    country_code = models.CharField(verbose_name="Kod państwa", max_length=2)
    country_name = models.CharField(verbose_name="Państwo", max_length=20)
    tsp_name = models.CharField(verbose_name="Dostawca usługi", max_length=255)
    tsp_service_name = models.CharField(verbose_name="Nazwa usługi", max_length=255)
    tsp_service_type = models.CharField(verbose_name="Typ usługi", max_length=100, default="")
    tsp_service_status = models.CharField(verbose_name="Status usługi", max_length=50, choices=TspServiceStatus.choices)
    tsp_service_start_date = models.DateTimeField(verbose_name="Start usługi")
    tsp_url = models.CharField(verbose_name="TSP URL", max_length=150, default="")
    crl_url = models.URLField(verbose_name="CRL URL", max_length=150, default="")
    tsp_service_digital_id = models.TextField(verbose_name="ID usługi", default="")
    service_status_app = models.CharField(
        verbose_name="Status obsługi",
        max_length=100,
        choices=ServiceStatus.choices,
    )
    crl_url_status_app = models.CharField(verbose_name="Status CRL URL", max_length=50, choices=CrlUrlStatus.choices)

    def __str__(self):
        return "TSP: " + str(self.tsp_name) + " — Service: " + str(self.tsp_service_name)


class TslValidityInfo(models.Model):
    country_code = models.CharField(verbose_name="Kod państwa", max_length=2)
    country_name = models.CharField(verbose_name="Państwo", max_length=20)
    tsl_operator_name = models.CharField(verbose_name="Nazwa operatora TSL", max_length=255)
    tsl_issue_date = models.DateTimeField(verbose_name="Data wydania TSL")
    tsl_expiry_date = models.DateTimeField(verbose_name="Data ważności TSL")
    tsl_validity_alert = models.CharField(verbose_name="Status TSL", max_length=100, default="")

    def __str__(self):
        return "Country: " + str(self.country_name) + " — TSL Operator Name: " + str(self.tsl_operator_name)
