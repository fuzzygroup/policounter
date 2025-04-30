from django.urls import path

from . import views

app_name = "counts"
urlpatterns = [
    path("", views.index, name="index"),
    # Event views
    path('events/', views.event_list, name='event_list'),
    path('events/<int:pk>/',       views.event_detail, name='event_detail'),
    path('events/add/', views.add_event, name='add_event'),
    # Observation view
    path('observations/<int:pk>/', views.observation_detail, name='observation_detail'),
    # Location views
    path('locations/', views.location_list, name='location_list'),
    path('locations/<int:location_id>/', views.location_events, name='location_events'),
]
