from django.db import models
from django.utils.translation import gettext_lazy as _


class TspServiceStatus(models.TextChoices):
    """
    Enumeration of technical service statuses.
    """
    GRANTED = "Granted", _("Granted")
    WITHDRAWN = "Withdrawn", _("Withdrawn")


class ServiceStatus(models.TextChoices):
    """
    Enumeration of internal service processing statuses, with Polish display labels.
    """
    NEW_NOT_SERVED = "Nie obsłużona (nowa)", _("Nie obsłużona (nowa)")
    WITHDRAWN_NOT_SERVED = "Nie obsłużona (wycofana)", _("Nie obsłużona (wycofana)")
    SERVED = "Obsłużona", _("Obsłużona")


class CrlUrlStatus(models.TextChoices):
    """
    Enumeration of CRL URL statuses for a service, in Polish.
    """
    URL_DEFINED = "CRL URL ustalony", _("CRL URL ustalony")
    URL_UNDEFINED = "CRL URL nieustalony", _("CRL URL nieustalony")
