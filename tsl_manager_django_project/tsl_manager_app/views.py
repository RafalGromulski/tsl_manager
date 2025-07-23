# from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.views.generic import DetailView, TemplateView, UpdateView, View

from tsl_manager_project.settings.development import DATA_DIRECTORY
from .choices import ServiceStatus, CrlUrlStatus
from .constants import COUNTRIES_PL
from .filters import MainViewFilter
from .forms import CrlUrlForm
from .models import TspServiceInfo, TslValidityInfo
from .services.service_updater import ServiceUpdater
from .services.tsl_parser import TslParser


class GreetingView(TemplateView):
    template_name = "greeting_view.html"


class FilteredServiceListView(LoginRequiredMixin, View):
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


class NewServicesView(FilteredServiceListView):
    template_name = "new_services.html"
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


class ProcessedServicesView(FilteredServiceListView):
    template_name = "processed_services.html"
    filter_kwargs = {"service_status_app": ServiceStatus.SERVED}
    order_by_fields = ["id", "country_name", "tsp_name"]


class ServiceDetailsView(LoginRequiredMixin, DetailView):
    model = TspServiceInfo
    template_name = "service_details.html"
    context_object_name = "tsp_service"


class ConfirmServiceView(LoginRequiredMixin, View):
    model = TspServiceInfo
    template_name = "confirm_service_modal_content.html"

    def get_object(self, pk):
        return get_object_or_404(self.model, pk=pk)

    def get(self, request, pk):
        tsp_object = self.get_object(pk)
        context = {"tsp_object": tsp_object}

        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            html = render_to_string("modals/confirm_service_modal_content.html", context, request=request)
            return JsonResponse({"html": html})

        return render(request, self.template_name, context)

    def post(self, request, pk):
        tsp_object = self.get_object(pk)
        tsp_object.service_status_app = ServiceStatus.SERVED
        tsp_object.save()

        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"success": True})

        return redirect("new_services")


class CrlUrlFormView(LoginRequiredMixin, UpdateView):
    model = TspServiceInfo
    template_name = "crl_url_form_modal_content.html"
    form_class = CrlUrlForm
    success_url = "/new_services/"

    def get_object(self, queryset=None):
        return get_object_or_404(self.model, pk=self.kwargs["pk"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tsp_object"] = self.object
        return context

    # def get_initial(self):
    #     initial = super().get_initial()
    #     initial["crl_url"] = self.object.crl_url
    #     return initial

    def form_valid(self, form):
        form.instance.service_status_app = ServiceStatus.SERVED
        form.instance.crl_url_status_app = CrlUrlStatus.URL_DEFINED

        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            form.save()
            return JsonResponse({"success": True})

        return super().form_valid(form)

    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            html = render_to_string("modals/crl_url_form_modal_content.html", context, request=self.request)
            return JsonResponse({"html": html})
        return super().render_to_response(context, **response_kwargs)


class TslStatusView(LoginRequiredMixin, TemplateView):
    model = TslValidityInfo
    template_name = "tsl_status.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tsp_services"] = self.model.objects.all().order_by("country_name")
        return context


class UpdateServicesView(LoginRequiredMixin, View):
    template_name = "update_services_modal_content.html"

    def post(self, request):
        parser = TslParser(DATA_DIRECTORY, COUNTRIES_PL)
        parsed_services = parser.parse_all()

        updater = ServiceUpdater(parsed_services)
        updater.run()

        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"success": True})

        return redirect("new_services")
