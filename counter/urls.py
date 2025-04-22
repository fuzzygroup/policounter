from django.urls import path

from . import views

app_name = "counts"
urlpatterns = [
    path("", views.index, name="index"),
    path("list/", views.prediction_list, name="list"),
    path("<int:pk>/", views.detail, name="detail"),
    path('estimate/', views.estimate, name='estimate')
]
