import logging

import numpy as np
logger = logging.getLogger(__name__)

import os
import uuid
from io import BytesIO

from PIL import Image
from django.shortcuts import get_object_or_404, render, redirect
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from django.views.generic import DetailView

from policounter import settings
from lwcc import LWCC

from .models import Location, Event, Observation, Prediction


def index(request):
    context = None
    return render(request, "counts/index.html", context)


def event_list(request):
    """View to display all events, sorted by most recent date first"""
    events = Event.objects.all().order_by('-date')
    return render(request, 'counts/event_list.html', {'events': events})

def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    observations = event.observations.all()  # thanks to related_name='observations'
    return render(request, 'counts/event_detail.html', {
        'event': event,
        'observations': observations,
    })

def observation_detail(request, observation_id):
    """View to display details of a specific observation, including prediction if available"""
    observation = get_object_or_404(Observation, pk=observation_id)
    return render(request, 'counts/observation_detail.html', {'observation': observation})


def prediction_detail(request, prediction_id):
    """View to display details of a specific prediction"""
    prediction = get_object_or_404(Prediction, pk=prediction_id)
    return render(request, 'counts/prediction_detail.html', {'prediction': prediction})


def location_list(request):
    """View to display all locations"""
    locations = Location.objects.all().order_by('country', 'state', 'city')
    return render(request, 'counts/location_list.html', {'locations': locations})


def location_events(request, location_id):
    """View to display events at a specific location"""
    location = get_object_or_404(Location, pk=location_id)
    events = location.events.all().order_by('-date')
    return render(request, 'counts/location_events.html', {
        'location': location,
        'events': events
    })
