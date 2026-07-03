from .models import Profile

def create_profile(backend, user, response, *args, **kwargs):
    if backend.name == 'steam':
        Profile.objects.get_or_create(
            user=user,
            defaults={'steam_id': response.get('player', {}).get('steamid', '')}
        )