from django.db import models

# Create your models here.
from django.db import models


class Player(models.Model):
    steamid = models.CharField(max_length=32, unique=True, db_index=True)
    persona_name = models.CharField(max_length=255, blank=True)
    profile_url = models.URLField(blank=True)
    avatar_url = models.URLField(blank=True)
    avatar_full_url = models.URLField(blank=True)
    country_code = models.CharField(max_length=5, blank=True)
    time_created = models.DateTimeField(null=True, blank=True)  # Steam account creation date

    last_synced = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.persona_name or self.steamid


class Group(models.Model):
    steam_group_id = models.CharField(max_length=32, unique=True, db_index=True)
    name = models.CharField(max_length=255, blank=True)
    url = models.URLField(blank=True)

    members = models.ManyToManyField(Player, blank=True, related_name='groups')

    def __str__(self):
        return self.name or self.steam_group_id


class Badge(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='badges')
    badge_id = models.PositiveIntegerField()
    level = models.PositiveSmallIntegerField(default=0)
    xp = models.PositiveIntegerField(default=0)
    completion_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('player', 'badge_id')

    def __str__(self):
        return f"Badge {self.badge_id} (level {self.level}) — {self.player}"


class Friend(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='friends')
    friend = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='friend_of')
    friends_since = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('player', 'friend')

    def __str__(self):
        return f"{self.player} ↔ {self.friend}"