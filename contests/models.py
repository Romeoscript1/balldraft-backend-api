from django.db import models
from datetime import timedelta,date
from django.utils import timezone
from django.urls import reverse
from django.utils.text import slugify
# from accounts.models import Profile
# from contest.models import Player
from django import forms

GAME_CHOICES = (
    ('NBA', 'NBA'),
    ('KFC', 'KFC'),
    ('EPL', 'EPL'),
)

class ContestCategory(models.Model):
    name = models.CharField(max_length=20)
    slug = models.SlugField(max_length=200,
                            unique=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
        ]
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self) -> str:
        return f'{self.name}'
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('game_list_by_category', args=[self.slug])
    
class ContestLevel(models.Model):
    level = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        ordering = ['level']
        indexes = [
            models.Index(fields=['level']),
        ]
        verbose_name = 'level'

    def __str__(self) -> str:
        return f'{self.level}'
    
    # def save(self, *args, **kwargs):
    #     self.slug = slugify(self.name)
    #     super().save(*args, **kwargs)
    
    # def get_absolute_url(self):
    #     return reverse('game_list_by_category', args=[self.slug])

class Contest(models.Model):
    category = models.ForeignKey(ContestCategory, on_delete=models.CASCADE, related_name='contestCat')
    level = models.ForeignKey(ContestLevel, on_delete=models.CASCADE, related_name='levels', default=1)
    title = models.CharField(max_length=250, null=True, blank=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    slug = models.SlugField(max_length=200, unique=True)
    start_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    end_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    max_entries = models.IntegerField(default=0,null=True,blank=True)
    entries = models.IntegerField(default=0,null=True,blank=True)

    entry_fee = models.IntegerField(default=0,null=True,blank=True)
    prize_pool = models.IntegerField(default=0,null=True,blank=True)
    management_fee = models.IntegerField(default=0,null=True,blank=True)
    total_salary = models.IntegerField(default=0)

    allow_multiple_entries = models.BooleanField(default=False)
    max_multi_entries = models.IntegerField(default=0,null=True,blank=True)

    is_live = models.BooleanField(default=False)
    is_upcoming = models.BooleanField(default=False)
    is_recommended = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title}"