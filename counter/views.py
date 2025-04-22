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

from policounter import settings
from lwcc import LWCC

from .models import Prediction
from .forms import PredictionForm


def index(request):
    prediction_list = Prediction.objects.order_by("-event_date")[:5]
    context = {"prediction_list": prediction_list}
    return render(request, "counts/index.html", context)

def detail(request, pk):
    prediction = get_object_or_404(Prediction, pk=pk)
    return render(request, 'counts/detail.html', {"prediction": prediction})

def estimate(request):
    if request.method == 'POST':
        form = PredictionForm(request.POST, request.FILES)
        if form.is_valid():
            session_id = uuid.uuid4().hex

            # probably janky -- I need the image before I can write the record
            uploaded_file = request.FILES['input_image']
            cacheDir = os.path.join(settings.MEDIA_ROOT, 'cache')
            fs = FileSystemStorage(location=cacheDir)
            filename = fs.save(f'{session_id}_{uploaded_file.name}', uploaded_file)
            input_image_path = fs.path(filename)

            # Perform prediction using input_image_path
            count, density = LWCC.get_count(
                input_image_path,
                return_density=True,
                model_name=form.cleaned_data['model_name'],
                model_weights=form.cleaned_data['weight_selection'],
                resize_img=False,
            )

            # Prepare the model instance
            prediction = form.save(commit=False)   # don't save or we'll error
            prediction.crowd_size_prediction = float(count)
            # this is bad but it works.  don't change.
            prediction.input_image.name = filename

            density_normalized = (density - density.min()) / (density.max() - density.min())
            density_uint8 = (density_normalized * 255).astype(np.uint8)
            density_image = Image.fromarray(density_uint8)

            # more jank but i have to have something in memory to write
            buffer = BytesIO()
            density_image.save(buffer, format='PNG')
            out_name = f'{session_id}_density_map.png'
            prediction.density_map.save(out_name, ContentFile(buffer.getvalue()), save=False)
            prediction.save()

            try:
                os.remove(input_image_path) # remove the cache file
            except OSError as e:
                # Log the error or handle it as needed
                print(f"Error deleting file {input_image_path}: {e}")

            return redirect('counts:detail', pk=prediction.pk)
    else:
        form = PredictionForm()
    return render(request, 'prediction_form.html', {'form': form})
