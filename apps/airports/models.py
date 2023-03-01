from django.db import models


# Create your models here.
class Airports(models.Model):
    iata = models.CharField(max_length=10, unique=True)
    location_name = models.CharField(max_length=200)
    city = models.CharField(max_length=200, null=True)
    country = models.CharField(max_length=200)

