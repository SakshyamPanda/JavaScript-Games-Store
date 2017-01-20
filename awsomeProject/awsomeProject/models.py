from django.db import models

class Product(models.Model):
    title = models.CharField(max_length=255)

class Game(models.Model):
    name = models.CharField(max_length=255, unique=True)
    url = models.URLField()
