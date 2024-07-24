from django.db import models
from datetime import timedelta,date
from django.utils import timezone
from django.urls import reverse
from django.utils.text import slugify
from profiles.models import Profile
from django import forms


class Player(models.Model):
    id = models.AutoField(primary_key=True)
    player_id = models.IntegerField(null=True)
    name = models.CharField(max_length=250)
    image_url = models.CharField(max_length=250)
    team_id = models.IntegerField(default=0)
    fixture_id = models.IntegerField(default=0)
    points = models.IntegerField(default=0)
    position = models.CharField(max_length=250, blank=True, null=True)

    def __str__(self):
        return self.name


class ContestHistory(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True, null=True)
    id = models.AutoField(primary_key=True)
    game_id = models.IntegerField()
    fixture_id = models.IntegerField(null=True)
    entry_amount = models.IntegerField(default=0)
    entered_by = models.DateTimeField(auto_now_add=True)
    league_name = models.CharField(max_length=150, blank=True, null=True)
    pending = models.BooleanField(default=True)
    completed = models.BooleanField(default=False)
    profit = models.BooleanField(default=False)
    players = models.ManyToManyField(Player, blank=True)
    total_points = models.FloatField(default=0.00)
    positions = models.BooleanField(default=False)
    position = models.IntegerField(default=0)
    max_entry = models.IntegerField(default=0)
    won_amount = models.DecimalField(decimal_places=2, max_digits=12, default=0.0)
    pool_price = models.IntegerField(default=0)


    def __str__(self):
        return f'{self.profile.username} - {self.name}'
