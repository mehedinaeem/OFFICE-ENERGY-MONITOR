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
