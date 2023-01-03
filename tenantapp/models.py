from django.db import models

# Create your models here.


class Hotels(models.Model):
    hotel_name = models.CharField(max_length=100)
