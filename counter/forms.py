from django import forms
from .models import Prediction

# Define choices as lists of tuples
VALID_MODELS = [
    ('CSRNet', 'CSRNet'),
    ('Bay', 'Bay'),
    ('DM-Count', 'DM-Count'),
    ('SFANet', 'SFANet'),
]

VALID_WEIGHTS = [
    ('SHA', 'SHA'),
    ('SHB', 'SHB'),
    ('QNRF', 'QNRF'),
]

class PredictionForm(forms.ModelForm):
    model_name = forms.ChoiceField(choices=VALID_MODELS, label='Model')
    weight_selection = forms.ChoiceField(choices=VALID_WEIGHTS, label='Weights')
    event_date = forms.DateField(
            widget=forms.DateInput(attrs={'type': 'date'}),
            label='Event Date'
        )
    class Meta:
        model = Prediction
        fields = [
            'input_image',
            'model_name',
            'weight_selection',
            'event_city',
            'event_date',
        ]
