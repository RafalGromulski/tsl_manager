from django.urls import path

from .views import (
    GreetingView,
    AllServicesView,
    NewServicesView,
    ProcessedServicesView,
    ServiceDetailsView,
    ConfirmServiceView,
    CrlUrlFormView,
    TslStatusView,
    UpdateServicesView,
)

urlpatterns = [
    path("", GreetingView.as_view(), name="greeting_view"),
    path("all-services/", AllServicesView.as_view(), name="all_services"),
    path("new_services/", NewServicesView.as_view(), name="new_services"),
    path("processed-services/", ProcessedServicesView.as_view(), name="processed_services"),
    path("service-details/<int:pk>/", ServiceDetailsView.as_view(), name="service_details"),
    path("confirm-service/<int:pk>/", ConfirmServiceView.as_view(), name="confirm_service"),
    path("crl-url-form/<int:pk>/", CrlUrlFormView.as_view(), name="crl_url_form"),
    path("tsl-status/", TslStatusView.as_view(), name="tsl_status"),
    path("update-services/", UpdateServicesView.as_view(), name="update_services"),
]
