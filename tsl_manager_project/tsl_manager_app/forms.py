from django.forms import (
    ModelForm,
    TextInput,
)

from .models import TspServiceInfo


class CrlUrlForm(ModelForm):
    """
    A form for updating the CRL URL field in the TspServiceInfo model.
    """

    class Meta:
        model = TspServiceInfo
        fields = ["crl_url"]
        labels = {
            "crl_url": ""
        }

        widgets = {
            "crl_url": TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter CRL URL"
            })
        }
