from django import forms
from .models import Event

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name', 'date']  # remove 'location'

    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
