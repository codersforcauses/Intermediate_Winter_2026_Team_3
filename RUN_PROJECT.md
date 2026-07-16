# Run Steam Stats locally

## 1. Backend

```bash
cd server
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Set a real `STEAM_API_KEY` in your shell or load the values from `.env`. Django reads environment variables directly; a shell example is:

```bash
export STEAM_API_KEY="your-key"
export DJANGO_SECRET_KEY="development-secret"
python manage.py migrate
python manage.py runserver
```

Backend: `http://localhost:8000`

## 2. Frontend

In a second terminal:

```bash
cd client
cp .env.example .env.local
npm ci
npm run dev
```

Frontend: `http://localhost:3000`

## Login and registration

Open `http://localhost:3000/login` and select **Sign in through Steam**. The first successful Steam login automatically creates the Django user, `Profile`, and linked `Player`, then attempts to synchronise public Steam library and friend data.

Steam game details and friend lists must be public for those statistics to be returned. The dashboard's **Sync Steam** button retries the synchronisation.

## Verification

```bash
cd server
source .venv/bin/activate
python manage.py check
python manage.py migrate --check
python manage.py test

cd ../client
npm run lint
npm run build
```
