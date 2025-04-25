import logging
from re import A

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

from .models import Prediction, PredictionGroup
from .forms import PredictionForm


def index(request):
    context = {"prediction_list": prediction_list}
    return render(request, "counts/index.html", context)

def prediction_detail(request, pk):
    prediction = get_object_or_404(Prediction, pk=pk)
    return render(request, 'counts/detail.html', {"prediction": prediction})

def group_detail(request, pk):
    group = get_object_or_404(PredictionGroup, pk=pk)
    predictions = group.predictions.all()
    return render(request, 'counts/group_detail.html', {
        'group': group,
        'predictions': predictions
    })

def prediction_list(request):
    groups = PredictionGroup.objects.all().order_by('-upload_date')
    return render(request, 'counts/prediction_list.html', {'group_list': groups})

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

            prediction_group = PredictionGroup.objects.create(
                            input_image=ContentFile(
                                fs.open(filename).read(),
                                name=filename
                            ),
                            event_city=form.cleaned_data['event_city'],
                            event_date=form.cleaned_data['event_date']
                        )

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
                        print(f"Error with model {model}, weight {weight}: {str(e)}")
                        # You could skip this prediction and continue with others
                        continue
                    # Prepare the model instance
                    prediction = form.save(commit=False)   # don't save or we'll error
                    prediction.crowd_size_prediction = float(count)
                    # this is bad but it works.  don't change.
                    prediction.input_image.name = filename
                    density_normalized = (density - density.min()) / (density.max() - density.min())
                    density_uint8 = (density_normalized * 255).astype(np.uint8)
                    density_image = Image.fromarray(density_uint8)
                    density_image_resized = density_image.resize(original_size)
            # more jank but i have to have something in memory to write
                    buffer = BytesIO()
                    density_image_resized.save(buffer, format='PNG')
                    out_name = f'{session_id}_density_map.png'
                    prediction = Prediction(
                         group=prediction_group,
                         model_name=model,
                         weight_selection=weight,
                         crowd_size_prediction=float(count)
                    )

                    prediction.density_map.save(out_name, ContentFile(buffer.getvalue()), save=False)

                    prediction.save()

            try:
                os.remove(input_image_path) # remove the cache file
            except OSError as e:
                # Log the error or handle it as needed
                print(f"Error deleting file {input_image_path}: {e}")

            return redirect('counts:group_detail', pk=prediction_group.pk)
    else:
        form = PredictionForm()
    return render(request, 'prediction_form.html', {'form': form})
