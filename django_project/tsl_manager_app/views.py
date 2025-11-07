from pathlib import Path
from typing import Any, Mapping, Protocol, cast

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.views.generic import DetailView, TemplateView, UpdateView, View

from .choices import CrlUrlStatus, ServiceStatus
from .constants import COUNTRIES_PL
from .filters import MainViewFilter
from .forms import CrlUrlForm
from .models import TslValidityInfo, TspServiceInfo
from .services.service_updater import ServiceUpdater
from .services.tsl_parser import TslParser


class GreetingView(TemplateView):
    template_name: str = "greeting_view.html"


class FilteredServiceListView(LoginRequiredMixin, View):
    model: type[TspServiceInfo] = TspServiceInfo
    template_name: str | None = None
    filter_kwargs: Mapping[str, Any] = {}
    order_by_fields: list[str] = []

    def get_queryset(self) -> QuerySet[TspServiceInfo]:
        return self.model.objects.filter(**self.filter_kwargs).order_by(*self.order_by_fields)

    def get(self, request: HttpRequest) -> HttpResponse:
        qs: QuerySet[TspServiceInfo] = self.get_queryset()
        my_filter = MainViewFilter(request.GET, queryset=qs)
        context: dict[str, Any] = {
            "my_filter": my_filter,
            "tsp_services": my_filter.qs,
        }
        template_name = cast(str, self.template_name)

        return render(request, template_name, context)


class NewServicesView(FilteredServiceListView):
    template_name: str = "new_services.html"
    filter_kwargs: Mapping[str, Any] = {
        "service_status_app__in": [
            ServiceStatus.NEW_NOT_SERVED,
            ServiceStatus.WITHDRAWN_NOT_SERVED,
        ]
    }
    order_by_fields: list[str] = ["country_name", "tsp_name", "tsp_service_name", "id"]


class AllServicesView(FilteredServiceListView):
    template_name: str = "all_services.html"
    order_by_fields: list[str] = ["country_name", "tsp_name", "tsp_service_name", "id"]


class ProcessedServicesView(FilteredServiceListView):
    template_name: str = "processed_services.html"
    filter_kwargs: Mapping[str, Any] = {"service_status_app": ServiceStatus.SERVED}
    order_by_fields: list[str] = ["id", "country_name", "tsp_name"]


class ServiceDetailsView(LoginRequiredMixin, DetailView):
    model = TspServiceInfo
    template_name: str = "service_details.html"
    context_object_name: str = "tsp_service"


class ConfirmServiceView(LoginRequiredMixin, View):
    model = TspServiceInfo
    template_name: str = "confirm_service_modal_content.html"

    def get_object(self, pk: int) -> TspServiceInfo:
        return get_object_or_404(self.model, pk=pk)

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        tsp_object = self.get_object(pk)
        context: dict[str, Any] = {"tsp_object": tsp_object}

        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            html: str = render_to_string("modals/confirm_service_modal_content.html", context, request=request)
            return JsonResponse({"html": html})

        return render(request, self.template_name, context)

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        tsp_object = self.get_object(pk)
        tsp_object.service_status_app = ServiceStatus.SERVED
        tsp_object.save()

        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"success": True})

        return redirect("new_services")


class CrlUrlFormView(LoginRequiredMixin, UpdateView):
    model = TspServiceInfo
    template_name: str = "crl_url_form_modal_content.html"
    form_class = CrlUrlForm
    success_url: str = "/new_services/"

    def get_object(self, queryset: QuerySet[TspServiceInfo] | None = None) -> TspServiceInfo:
        return get_object_or_404(self.model, pk=self.kwargs["pk"])

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["tsp_object"] = self.object
        return context

    def form_valid(self, form: CrlUrlForm) -> HttpResponse:
        form.instance.service_status_app = ServiceStatus.SERVED
        form.instance.crl_url_status_app = CrlUrlStatus.URL_DEFINED

        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            form.save()
            return JsonResponse({"success": True})

        return super().form_valid(form)

    def render_to_response(self, context: dict[str, Any], **response_kwargs: Any) -> HttpResponse:
        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            html: str = render_to_string("modals/crl_url_form_modal_content.html", context, request=self.request)
            return JsonResponse({"html": html})
        return super().render_to_response(context, **response_kwargs)


class TslStatusView(LoginRequiredMixin, TemplateView):
    model = TslValidityInfo
    template_name: str = "tsl_status.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["tsp_services"] = self.model.objects.all().order_by("country_name")
        return context


class _SettingsWithDataDir(Protocol):
    DATA_DIRECTORY: Path


class UpdateServicesView(LoginRequiredMixin, View):
    template_name: str = "update_services_modal_content.html"

    def post(self, request: HttpRequest) -> HttpResponse:
        _settings = cast(_SettingsWithDataDir, cast(object, settings))
        data_dir: Path = _settings.DATA_DIRECTORY

        parser = TslParser(data_dir, COUNTRIES_PL)
        parsed_services = parser.parse_all()

        updater = ServiceUpdater(parsed_services)
        updater.run()

        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"success": True})

        return redirect("new_services")
