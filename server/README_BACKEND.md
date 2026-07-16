# Steam Stats Django Backend

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Export the environment values from `.env`, then run:

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Main API endpoints

- `GET/PATCH /api/profile/me/`
- `GET /api/dashboard/`
- `POST /api/steam/sync/`
- `GET /api/steam/games/`
- `GET /api/steam/games/<steam_appid>/`
- `GET/POST /api/steam/games/<steam_appid>/achievements/`
- `GET /api/steam/friends/`
- `GET /api/steam/news/`

All endpoints require a logged-in Django session. Steam login starts at `/auth/login/steam/`.
