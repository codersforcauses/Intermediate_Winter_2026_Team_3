import logging

from .models import Profile
from players.models import Player

logger = logging.getLogger(__name__)


def create_profile(backend, user, uid=None, response=None, *args, **kwargs):
    """Create/link the local account after Steam OpenID authentication.

    python-social-auth creates the Django User earlier in the pipeline. This
    step stores the Steam identity and performs a best-effort initial sync so
    a newly registered user reaches a populated dashboard.
    """
    if backend.name != "steam":
        return

    response = response or {}
    player_data = response.get("player", {})
    steamid = str(uid or player_data.get("steamid") or "").strip()
    if not steamid:
        logger.warning("Steam login completed without a Steam ID for user %s", user.pk)
        Profile.objects.get_or_create(user=user)
        return

    player, _ = Player.objects.update_or_create(
        steamid=steamid,
        defaults={
            "persona_name": player_data.get("personaname", ""),
            "profile_url": player_data.get("profileurl", ""),
            "avatar_url": player_data.get("avatar", ""),
            "avatar_full_url": player_data.get("avatarfull", ""),
            "country_code": player_data.get("loccountrycode", ""),
        },
    )

    profile, _ = Profile.objects.get_or_create(user=user)
    if profile.player_id != player.id:
        profile.player = player
        profile.save(update_fields=["player"])

    # Avoid failing the login flow when Steam is temporarily unavailable or
    # the account's game/friend details are private.
    try:
        from games.services import sync_player_friends, sync_player_library
        from players.services import SteamAPIError

        result = sync_player_library(player)
        try:
            result.update(sync_player_friends(player))
        except SteamAPIError:
            logger.info("Friend sync unavailable for Steam user %s", steamid)

        profile.last_synced = result.get("last_synced")
        profile.save(update_fields=["last_synced"])
    except Exception:  # login must still succeed; explicit sync can be retried later
        logger.exception("Initial Steam sync failed for Steam user %s", steamid)
