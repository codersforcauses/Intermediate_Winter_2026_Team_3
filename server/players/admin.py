from django.contrib import admin
from .models import Badge, Friend, Group, Player

admin.site.register(Player)
admin.site.register(Group)
admin.site.register(Badge)
admin.site.register(Friend)
