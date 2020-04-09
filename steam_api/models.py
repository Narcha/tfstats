from django.db import models

# Create your models here.
class PlayerStats(models.Model):
    timestamp = models.DateTimeField()
    json_string = models.TextField()