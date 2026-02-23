from django.urls import path
from .views import DistributorCreateAPIView, DistributorListAPIView

urlpatterns = [
    path("", DistributorListAPIView.as_view(), name="distributor-list"),
    path("create/", DistributorCreateAPIView.as_view(), name="create-distributor"),
]