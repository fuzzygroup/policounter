import logging

import numpy as np
logger = logging.getLogger(__name__)

import os
import uuid
from io import BytesIO

from PIL import Image
from django.shortcuts import get_object_or_404, render, redirect
from django.core.serializers import serialize
from django.http import JsonResponse
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from django.views.generic import DetailView

from policounter import settings
from lwcc import LWCC

from .models import Location, Event, Observation
from .forms import EventForm


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

def observation_detail(request, pk):
    """View to display details of a specific observation, including prediction if available"""
    observation = get_object_or_404(Observation, pk=pk)
    return render(request, 'counts/observation_detail.html', {'observation': observation})


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


def add_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            # Add location manually
            location_id = request.POST.get('location')
            location = Location.objects.get(pk=location_id)
            event = form.save(commit=False)
            event.location = location
            event.save()
            return redirect('counts:event_list')
    else:
        form = EventForm()

    # Prepare JSON for all locations
    locations = Location.objects.all().values('pk', 'city', 'state', 'country')
    return render(request, 'counts/add_event.html', {
        'form': form,
        'locations_json': list(locations),
    })
