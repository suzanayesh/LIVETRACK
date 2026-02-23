from django.urls import path

from .views import (BulkCreateCustomersAPI, CreateCustomerAPI,
                    CustomerDetailAPI, ListCustomersAPI,
                    ListCustomersAPIByPhone)

urlpatterns = [
    path("", CreateCustomerAPI.as_view(), name="create-customer"),
    path("list/", ListCustomersAPI.as_view(), name="list-customers"),
    path("listbyphone/", ListCustomersAPIByPhone.as_view(), name="list-customers-by-phone"),
    path("bulk-create/", BulkCreateCustomersAPI.as_view(), name="bulk-create-customers"),
    path("<int:customer_id>/", CustomerDetailAPI.as_view(), name="customer-detail"),
    path("<int:customer_id>/", CustomerDetailAPI.as_view(), name="customer-detail"),
]