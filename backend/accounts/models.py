
# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    last_synced = models.DateTimeField(null=True, blank=True)
    is_public_profile = models.BooleanField(default=True)
    preferred_currency = models.CharField(max_length=10, default="USD")
    steam_id = models.CharField(max_length=20, unique=True, blank=True, null=True, db_index=True)

    def __str__(self):
        return self.user.username