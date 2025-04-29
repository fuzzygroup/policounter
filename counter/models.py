from django.db import models


class Location(models.Model):
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.city}, {self.state}, {self.country}"

    class Meta:
        unique_together = ['city', 'state', 'country']


class Event(models.Model):
    name = models.CharField(max_length=200)
    date = models.DateField()
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='events')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} on {self.date.strftime('%Y-%m-%d')} at {self.location.city}"

    class Meta:
        unique_together = ['name', 'date', 'location']


class Observation(models.Model):
    METHOD_CHOICES = [
        ('CLICKER', 'Hand count using clicker'),
        ('EYEBALL', 'Eyeball estimate'),
        ('AI', 'AI model prediction'),
    ]

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='observations')
    count = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField()
    method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    observer = models.CharField(max_length=100, blank=True, null=True)
    # New fields moved from Prediction:
    input_image = models.ImageField(upload_to='inputs', blank=True, null=True)
    density_map = models.ImageField(upload_to='density_maps', blank=True, null=True)
    model_name = models.CharField(max_length=50, blank=True, null=True)
    weight_selection = models.CharField(max_length=20, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.method == 'AI':
            return f"AI Observation ({self.model_name}) - {self.event.name}"
        return f"{self.get_method_display()} by {self.observer or 'Unknown'} - {self.event.name}"
