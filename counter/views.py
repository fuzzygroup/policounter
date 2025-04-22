from django.shortcuts import get_object_or_404, render
from .models import Prediction

def index(request):
    prediction_list = Prediction.objects.order_by("-event_date")[:5]
    context = {"prediction_list": prediction_list}
    return render(request, "counts/index.html", context)

def detail(request, pk):
    prediction = get_object_or_404(Prediction, pk=pk)
    return render(request, 'counts/detail.html', {"prediction": prediction})
