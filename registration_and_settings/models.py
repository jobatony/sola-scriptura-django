import random
import string
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    pass
    # Add custom fields here if needed, e.g.,
    # is_moderator = models.BooleanField(default=False)

class UserSettings(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='settings')
    theme = models.CharField(max_length=20, default='light')
    notifications_enabled = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username}'s settings"

class Competition(models.Model):
    name = models.CharField(max_length=200)
    church_name = models.CharField(max_length=200)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='competitions')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)
    number_of_rounds = models.IntegerField(default=3)
    
    def __str__(self):
        return f"{self.name} - {self.church_name}"

class Participant(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('eliminated', 'Eliminated'),
    ]
    
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name='participants')
    full_name = models.CharField(max_length=200)
    age = models.IntegerField(null=True, blank=True)
    unit_fellowship = models.CharField(max_length=200, blank=True)
    email = models.EmailField(null=True, blank=True)
    
    # The unique 4-digit code for the user to join
    access_code = models.CharField(max_length=4, unique=True, editable=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    score = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.access_code:
            self.access_code = self._generate_unique_code()
        super().save(*args, **kwargs)

    def _generate_unique_code(self):
        """Generates a unique 4-digit code."""
        while True:
            code = ''.join(random.choices(string.digits, k=4))
            if not Participant.objects.filter(access_code=code).exists():
                return code

    def __str__(self):
        return f"{self.full_name} ({self.access_code})"