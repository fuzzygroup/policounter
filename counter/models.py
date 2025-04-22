from django.db import models

class Prediction(models.Model):
    input_image = models.ImageField(upload_to='inputs')
    density_map = models.ImageField(upload_to='density_maps')
    model_name = models.CharField(max_length=10)
    weight_selection = models.CharField(max_length=4)
    crowd_size_prediction = models.DecimalField(max_digits=10, decimal_places=2)
    event_city = models.CharField(max_length=100)
    event_date = models.DateField()
    prediction_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.model_name} ({self.weight_selection}) – {self.event_city} on {self.prediction_date.strftime('%Y-%m-%d')}"
