from django.urls import path
from .views import (
    HotelView
)

urlpatterns = [
    path('hotel', HotelView.as_view())
]
