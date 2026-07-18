# Completed backend additions

Implemented a normalized Django database and REST API for Steam statistics.

## Database additions

- `games_usergame`: player-owned games and per-platform playtime
- `games_playtimesnapshot`: historical playtime snapshots for graphs
- `games_playerachievement`: per-player achievement completion
- Expanded game, achievement and news metadata
- Existing player, friend, badge, group and account profile tables retained

## Backend additions

- Steam Web API client
- Player profile/library/friend/achievement synchronization services
- Session-authenticated REST API serializers and views
- Dashboard summary API
- Game library, game detail, achievement, friend and news endpoints
- CORS and CSRF configuration for a Next.js frontend on localhost:3000
- Environment-based secrets and Steam API key
- Requirements and setup documentation

The included SQLite database is a clean migrated development database. Create a superuser and sign in through Steam before using personal endpoints.
