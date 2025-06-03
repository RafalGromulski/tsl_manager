from django.urls import path
# from rest_framework import routers  # TODO: Enable if ViewSets are used

from .views import (
    GreetingView,
    AllServicesView,
    ServicesToServedView,
    ServedServicesView,
    ServiceDetailsView,
    ConfirmServiceView,
    CrlUrlFormView,
    TslValidityView,
    UpdateServicesView,
    # TspServiceViewSet,
)

# router = routers.DefaultRouter()
# router.register(r"crl_urls", TspServiceViewSet)

urlpatterns = [
    path("", GreetingView.as_view(), name="greeting_view"),
    path("all-services/", AllServicesView.as_view(), name="all_services"),
    path("services-to-served/", ServicesToServedView.as_view(), name="services_to_served"),
    path("served-services/", ServedServicesView.as_view(), name="served_services"),
    path("service-details/<int:pk>/", ServiceDetailsView.as_view(), name="service_details"),
    path("confirm-service/<int:pk>/", ConfirmServiceView.as_view(), name="confirm_service"),
    path("crl-url-form/<int:pk>/", CrlUrlFormView.as_view(), name="crl_url_form"),
    path("tsl-validity/", TslValidityView.as_view(), name="tsl_validity"),
    path("update-services/", UpdateServicesView.as_view(), name="update_services"),
    # path("api/", include(router.urls)),
]
