from django.contrib import admin
from .models import Location, Event, Observation

admin.site.register(Location)
admin.site.register(Event)
admin.site.register(Observation)
# Register your models here.
