from django.urls import path,include
from django.contrib import admin
from multi_tenant.views import HomeView
# from rest_framework import routers



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomeView.as_view())
    # path('', include('customers.urls'))

]
