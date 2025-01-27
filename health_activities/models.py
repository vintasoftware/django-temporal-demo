from django.contrib.auth.models import User
from django.db import models


class HealthActivity(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    duration = models.PositiveIntegerField()  # in seconds
    calories_burned = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='health_activities')

    def __str__(self):
        duration_in_minutes = self.duration / 60
        return f"{self.name} ({duration_in_minutes:.2f} mins) - {self.calories_burned}kcals - {self.user}"


class CaloriesPerMonth(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    month = models.PositiveIntegerField(db_index=True)
    year = models.PositiveIntegerField(db_index=True)
    calories = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.user} - {self.month}/{self.year}: {self.calories}kcals"
