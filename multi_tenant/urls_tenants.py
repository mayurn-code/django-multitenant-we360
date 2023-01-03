from customers.views import TenantView
from tenantapp.views import HotelView
from django.urls import path,include

urlpatterns = [
    path('',include('customers.urls')),
    path('tenant/',include('tenantapp.urls'))
]
