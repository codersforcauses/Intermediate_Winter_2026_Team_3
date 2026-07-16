from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from .models import Friend
from .serializers import FriendSerializer


class MyFriendsView(ListAPIView):
    serializer_class = FriendSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Friend.objects.select_related("friend").filter(player=self.request.user.profile.player)
