import logging

import numpy as np
logger = logging.getLogger(__name__)

import os
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
            uploaded_file = request.FILES['input_image']
            fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'inputs'))
            filename = fs.save(uploaded_file.name, uploaded_file)
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
            prediction = form.save(commit=False)
            prediction.crowd_size_prediction = float(count)
            prediction.input_image.name = os.path.join('inputs', filename)
            prediction.save()

            density_normalized = (density - density.min()) / (density.max() - density.min())
            density_uint8 = (density_normalized * 255).astype(np.uint8)
            density_image = Image.fromarray(density_uint8, mode='L')  # 'L' mode for grayscale

            buffer = BytesIO()
            density_image.save(buffer, format='PNG')
            prediction.density_map.save(uploaded_file.name, ContentFile(buffer.getvalue()), save=False)


            prediction.save()
            return redirect('counts:detail', pk=prediction.pk)
    else:
        form = PredictionForm()
    return render(request, 'prediction_form.html', {'form': form})
