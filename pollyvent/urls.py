from django.urls import path
from .views import generate_flyer_view

urlpatterns = [
    path("generate-flyer/", generate_flyer_view, name="generate_flyer"),
]
