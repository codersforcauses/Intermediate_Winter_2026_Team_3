from .models import Profile
from players.models import Player


from .models import Profile
from players.models import Player


def create_profile(backend, user, response, *args, **kwargs):
    if backend.name == 'steam':
        steamid = response.get('player', {}).get('steamid', '')

        player = None
        if steamid:
            player, _ = Player.objects.get_or_create(steamid=steamid)

        profile, _ = Profile.objects.get_or_create(
            user=user,
            defaults={'player': player}
        )

        if player and profile.player_id != player.id:
            profile.player = player
            profile.save()