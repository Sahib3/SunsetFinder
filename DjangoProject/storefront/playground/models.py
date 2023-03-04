from django.db import models

# Create your models here.
#model for the object that
class SunsetLocation(models.Model):
    lattitude=models.FloatField()
    longitude=models.FloatField()
