from django.http import HttpResponse
from django.template import loader
from .models import Prediction


def index(request):
    prediction_list = Prediction.objects.order_by("-event_date")[:5]
    template = loader.get_template('counts/index.html')
    context = {"prediction_list": prediction_list}
    return HttpResponse(template.render(context, request))


def detail(request, pk):
    return HttpResponse("You're looking at prediction %s." % pk)
