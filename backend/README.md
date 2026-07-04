# Office Energy Monitor Backend

Django + Django REST Framework backend for the Office Energy Monitor project.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_devices
python manage.py runserver
```

Copy `backend/.env.example` if you want to configure production-like settings locally:

```bash
cp .env.example .env
```

## Useful Commands

Run tests:

```bash
python manage.py test
```

Run simulator:

```bash
python manage.py simulate_devices
```

Create or refresh dummy office data:

```bash
python manage.py seed_devices
```

## Main API Endpoints

- `GET /api/health/`
- `GET /api/snapshot/`
- `GET /api/status-summary/`
- `GET /api/devices/`
- `POST /api/devices/<id>/toggle/`
- `GET /api/rooms/<slug>/`
- `GET /api/usage/`
- `GET /api/alerts/`

## Data Notes

The backend uses SQLite and dummy seeded data for the current MVP. It is the single source of truth for the React dashboard, simulator, manual toggles, and future Discord bot.

## Render Deployment

The backend is prepared for Render with:

- `build.sh`
- `Procfile`
- environment-based Django settings
- WhiteNoise static file support
- optional PostgreSQL through `DATABASE_URL`

Manual Render settings:

```text
Root Directory: backend
Build Command: ./build.sh
Start Command: python manage.py migrate --noinput && python manage.py seed_devices && gunicorn config.wsgi:application
```

Required Render environment variables:

```env
DJANGO_SECRET_KEY=generate-a-secure-secret
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=your-render-service.onrender.com
CORS_ALLOWED_ORIGINS=https://your-netlify-site.netlify.app
CSRF_TRUSTED_ORIGINS=https://your-netlify-site.netlify.app
DATABASE_URL=your-render-postgres-connection-string
```
