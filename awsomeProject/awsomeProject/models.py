from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    title = models.CharField(max_length=255)

class Game(models.Model):
    name = models.CharField(max_length=255, unique=True)
    url = models.URLField()

class Scores(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey('Game', on_delete=models.CASCADE)
    score = models.FloatField()

class Gameplay(models.Model):
    #TODO: user and game should be unique as combination if possible
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.FloatField()
    game = models.ForeignKey('Game', on_delete=models.CASCADE)

class PlayerItem(models.Model):
    gameplay = models.ForeignKey('Gameplay', on_delete=models.CASCADE)
    itemName = models.CharField(max_length=255)
