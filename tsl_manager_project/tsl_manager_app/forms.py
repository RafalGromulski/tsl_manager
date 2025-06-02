from django.forms import (
    ModelForm,
    TextInput,
)

from .models import TspServiceInfo


class CrlUrlForm(ModelForm):
    class Meta:
        model = TspServiceInfo
        fields = ["crl_url"]
        labels = {"crl_url": False}
        widgets = {"crl_url": TextInput(attrs={"class": "form-control", "placeholder": "Wpisz CRL URL"})}
