from django.db import models
from django.utils.translation import gettext_lazy as _


class TspServiceStatus(models.TextChoices):
    GRANTED = "Granted"
    WITHDRAWN = "Withdrawn"


class ServiceStatus(models.TextChoices):
    NEW_NOT_SERVED = "Nie obsłużona (nowa)", _("Nie obsłużona (nowa)")
    WITHDRAWN_NOT_SERVED = "Nie obsłużona (wycofana)", _("Nie obsłużona (wycofana)")
    SERVED = "Obsłużona", _("Obsłużona")


class CrlUrlStatus(models.TextChoices):
    URL_DEFINED = "CRL URL ustalony", _("CRL URL ustalony")
    URL_UNDEFINED = "CRL URL nieustalony", _("CRL URL nieustalony")
