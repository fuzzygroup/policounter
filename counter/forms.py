from django import forms
from .models import Event, Observation
from django.utils import timezone


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name', 'date']  # remove 'location'

    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))


class ObservationForm(forms.ModelForm):
    class Meta:
        model = Observation
        fields = ['count', 'observer', 'input_image']
        widgets = {
            'count': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'observer': forms.TextInput(attrs={'class': 'form-control'}),
            'input_image': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(ObservationForm, self).__init__(*args, **kwargs)
        # Mark fields as not required if they can be blank/null
        if self.fields.get('observer'):
            self.fields['observer'].required = False
        if self.fields.get('input_image'):
            self.fields['input_image'].required = False

    def save(self, commit=True, event=None):
        instance = super(ObservationForm, self).save(commit=False)

        # Set method to either CLICKER or EYEBALL based on whether an image was provided
        instance.method = 'EYEBALL'
        if instance.input_image:
            instance.method = 'CLICKER'

        # Set event from parameter
        if event:
            instance.event = event

        # Set timestamp to current time
        instance.timestamp = timezone.now()

        if commit:
            instance.save()
        return instance
