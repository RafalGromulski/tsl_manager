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
    Enumeration of internal service processing statuses.
    """

    NEW_NOT_SERVED = "Not served (new)", _("Not served (new)")
    WITHDRAWN_NOT_SERVED = "Not served (withdrawn)", _("Not served (withdrawn)")
    SERVED = "Served", _("Served")


class CrlUrlStatus(models.TextChoices):
    """
    Enumeration of CRL URL statuses for a service.
    """

    URL_DEFINED = "CRL URL defined", _("CRL URL defined")
    URL_UNDEFINED = "CRL URL undefined", _("CRL URL undefined")
