from django.contrib import admin
from .models import Location, Event, Observation, Prediction

admin.site.register(Location)
admin.site.register(Event)
admin.site.register(Observation)
admin.site.register(Prediction)
# Register your models here.
