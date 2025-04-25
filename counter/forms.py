from django import forms
from .models import PredictionGroup

class PredictionForm(forms.ModelForm):
    event_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='Event Date'
    )

    class Meta:
        model = PredictionGroup
        fields = [
            'input_image',
            'event_city',
            'event_date',
        ]
