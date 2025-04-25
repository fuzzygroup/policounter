from django.urls import path

from . import views

app_name = "counts"
urlpatterns = [
    path("", views.index, name="index"),
    path('predictions/', views.prediction_list, name='prediction_list'),
    path('prediction/<int:pk>/', views.prediction_detail, name='detail'),
    path('group_detail/<int:pk>/', views.group_detail, name='group_detail'),
    path('estimate/', views.estimate, name='estimate'),
]
