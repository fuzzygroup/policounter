import logging

import numpy as np
logger = logging.getLogger(__name__)

import os
import uuid
from io import BytesIO
from PIL import Image

from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator

from policounter import settings
from lwcc import LWCC

from .models import Location, Event, Observation
from .forms import EventForm, ObservationForm, PredictionForm


def index(request):
    context = None
    return render(request, "counts/index.html", context)

def event_list(request):
    event_list = Event.objects.all().order_by('-date')  # Get all events (you can filter them as needed)
    paginator = Paginator(event_list, 10)  # Show 10 events per page
    page_number = request.GET.get('page')  # Get the current page from the URL
    events = paginator.get_page(page_number)  # Get the events for the current page
    return render(request, 'counts/event_list.html', {'events': events})

def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    observations = event.observations.order_by('-timestamp')  # Get all observations, ordered by timestamp
    paginator = Paginator(observations, 10)  # Paginate observations (10 per page)
    page_number = request.GET.get('page')  # Get the current page from the URL
    observations_page = paginator.get_page(page_number)  # Get the observations for the current page

    return render(request, 'counts/event_detail.html', {
        'event': event,
        'observations': observations_page,  # Pass the paginated observations
    })

def observation_detail(request, pk):
    """View to display details of a specific observation, including prediction if available"""
    observation = get_object_or_404(Observation, pk=pk)
    return render(request, 'counts/observation_detail.html', {'observation': observation})

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
            return redirect('counts:event_detail', pk=event.pk)
    else:
        form = EventForm()

    # Prepare JSON for all locations
    locations = Location.objects.all().values('pk', 'city', 'state', 'country')
    return render(request, 'counts/add_event.html', {
        'form': form,
        'locations_json': list(locations),
    })

def add_observation(request, event_id):
    event = get_object_or_404(Event, pk=event_id)

    if request.method == 'POST':
        form = ObservationForm(request.POST, request.FILES)
        if form.is_valid():
            observation = form.save(commit=False, event=event)
            observation.save()
            messages.success(request, "Observation added successfully!")
            return redirect('counts:event_detail', pk=event.id)
    else:
        form = ObservationForm()

    return render(request, 'counts/add_observation.html', {
        'form': form,
        'event': event,
    })

def estimate(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    if request.method == 'POST':
        form = PredictionForm(request.POST, request.FILES)
        if form.is_valid():
            session_id = uuid.uuid4().hex
            uploaded_file = request.FILES['input_image']
            cacheDir = os.path.join(settings.MEDIA_ROOT, 'cache')
            fs = FileSystemStorage(location=cacheDir)
            filename = fs.save(f'{session_id}_{uploaded_file.name}', uploaded_file)
            input_image_path = fs.path(filename)
            # Load the original image to get its size
            original_image = Image.open(input_image_path)
            original_size = original_image.size  # (width, height)
            # Define choices as lists of tuples
            VALID_MODELS = [
                'CSRNet',
                'Bay',
                'DM-Count',
                'SFANet',
            ]
            VALID_WEIGHTS = [
                'SHA',
                'SHB',
                'QNRF',
            ]
            try:
                for model in VALID_MODELS:
                    for weight in VALID_WEIGHTS:
                        try:
                            count, density = LWCC.get_count(
                                input_image_path,
                                return_density=True,
                                model_name=model,
                                model_weights=weight,
                                resize_img=False,
                            )
                        except ValueError as e:
                            # Log the error
                            continue  # Skip to the next iteration

                        prediction = form.save(commit=False)  # don't save or we'll error
                        prediction.crowd_size_prediction = float(count)
                        # this is bad but it works. don't change.
                        prediction.input_image.name = filename
                        density_normalized = (density - density.min()) / (density.max() - density.min())
                        density_uint8 = (density_normalized * 255).astype(np.uint8)
                        density_image = Image.fromarray(density_uint8)
                        density_image_resized = density_image.resize(original_size)
                        # more jank but i have to have something in memory to write
                        buffer = BytesIO()
                        density_image_resized.save(buffer, format='PNG')
                        out_name = f'{session_id}_density_map.png'
                        prediction = Observation(
                            event=event,
                            method='AI prediction',
                            model_name=model,
                            weight_selection=weight,
                            count=float(count),
                        )
                        prediction.density_map.save(out_name, ContentFile(buffer.getvalue()), save=False)
                        prediction.save()

                # Move the file deletion outside the inner loop but inside the outer try block
                # (after all models and weights have been processed)
                if os.path.exists(input_image_path):
                    os.remove(input_image_path)  # remove the cache file

                # Redirect to the event detail page after successful processing
                # Hardcoding the URL to match your URL patterns
                return redirect(f'/events/{event_id}/')
            except Exception as e:
                # Catch any unexpected exceptions
                print(f"Error processing file: {e}")
                # Still try to clean up if possible
                if 'input_image_path' in locals() and os.path.exists(input_image_path):
                    try:
                        os.remove(input_image_path)
                    except OSError as e:
                        print(f"Error deleting file {input_image_path}: {e}")
                messages.error(request, "An error occurred while processing the image.")
    else:
        form = PredictionForm()

    return render(request, 'prediction_form.html', {'form': form, 'event': event})
