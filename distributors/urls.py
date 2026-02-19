from django.urls import path

from .views import DistributorCreateView

urlpatterns = [
    path("", DistributorCreateView.as_view(), name="create-distributor"),
]
