
# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from players.models import Player

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    player = models.OneToOneField(
    Player,
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='account_profile'
    )
    last_synced = models.DateTimeField(null=True, blank=True)
    is_public_profile = models.BooleanField(default=True)
    preferred_currency = models.CharField(max_length=10, default="USD")

    def __str__(self):
        return self.user.username
    
