from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import DetailView, TemplateView, UpdateView, View

# from rest_framework import viewsets

from .choices import ServiceStatus, CrlUrlStatus
from .constants import COUNTRIES_PL
from .filters import MainViewFilter
from .forms import CrlUrlForm
from .models import TspServiceInfo, TslValidityInfo
# from .serializers import TspServiceInfoSerializer
from .services.tsl_parser import TslParser, ServiceUpdater


class GreetingView(TemplateView):
    template_name = "greeting_view.html"


# class FilteredServiceListView(LoginRequiredMixin, View):
class FilteredServiceListView(View):
    model = TspServiceInfo
    template_name = None
    filter_kwargs = {}
    order_by_fields = []

    def get_queryset(self):
        return self.model.objects.filter(**self.filter_kwargs).order_by(*self.order_by_fields)

    def get(self, request):
        qs = self.get_queryset()
        my_filter = MainViewFilter(request.GET, queryset=qs)
        context = {
            "my_filter": my_filter,
            "tsp_services": my_filter.qs,
        }
        return render(request, self.template_name, context)


class ServicesToServedView(FilteredServiceListView):
    # template_name = "services_to_served.html"
    filter_kwargs = {
        "service_status_app__in": [
            ServiceStatus.NEW_NOT_SERVED,
            ServiceStatus.WITHDRAWN_NOT_SERVED,
        ]
    }
    order_by_fields = ["country_name", "tsp_name", "tsp_service_name", "id"]


class AllServicesView(FilteredServiceListView):
    template_name = "all_services.html"
    order_by_fields = ["country_name", "tsp_name", "tsp_service_name", "id"]


class ServedServicesView(FilteredServiceListView):
    template_name = "served_services.html"
    filter_kwargs = {"service_status_app": ServiceStatus.SERVED}
    order_by_fields = ["id", "country_name", "tsp_name"]


class ServiceDetailsView(LoginRequiredMixin, DetailView):
    model = TspServiceInfo
    template_name = "service_details.html"
    context_object_name = "tsp_service"


class ConfirmServiceView(LoginRequiredMixin, View):
    model = TspServiceInfo
    template_name = "confirm_service.html"

    def get_object(self, pk):
        return get_object_or_404(self.model, pk=pk)

    def get(self, request, pk):
        tsp_object = self.get_object(pk)
        return render(request, self.template_name, {"tsp_object": tsp_object})

    def post(self, request, pk):
        tsp_object = self.get_object(pk)
        tsp_object.service_status_app = ServiceStatus.SERVED
        tsp_object.save()
        return redirect("services_to_served")


class CrlUrlFormView(LoginRequiredMixin, UpdateView):
    model = TspServiceInfo
    template_name = "crl_url_form.html"
    form_class = CrlUrlForm
    success_url = "/services_to_served/"

    def get_object(self, queryset=None):
        return get_object_or_404(self.model, pk=self.kwargs["pk"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tsp_object"] = self.object
        return context

    def get_initial(self):
        initial = super().get_initial()
        initial["crl_url"] = self.object.crl_url
        return initial

    def form_valid(self, form):
        form.instance.service_status_app = ServiceStatus.SERVED
        form.instance.crl_url_status_app = CrlUrlStatus.URL_DEFINED
        return super().form_valid(form)


class TslValidityView(LoginRequiredMixin, TemplateView):
    model = TslValidityInfo
    template_name = "tsl_validity.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tsp_services"] = self.model.objects.all().order_by("country_name")
        return context


class UpdateServicesView(LoginRequiredMixin, View):
    template_name = "update_services.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        parser = TslParser(settings.DATA_DIRECTORY, COUNTRIES_PL)
        service_data = parser.tsl_parse()

        updater = ServiceUpdater(service_data)
        updater.run()

        return redirect("services_to_served")


# class TspServiceViewSet(viewsets.ModelViewSet):
#     queryset = TspServiceInfo.objects.filter(crl_url__startswith="http")
#     serializer_class = TspServiceInfoSerializer
