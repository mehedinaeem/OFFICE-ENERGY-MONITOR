# Office Energy Monitor

Office Energy Monitor is a hackathon project for tracking simulated office device energy usage from a single backend API. The first version uses dummy data only; no real hardware integration is included yet.

## Planned Architecture

- `backend/`: Django + Django REST Framework API. This will be the single source of truth for rooms, devices, statuses, wattage, current power, timestamps, and alerts.
- `frontend/`: React + Vite dashboard. This will read from the backend API and update live without manual refresh.
- `docs/`: Project notes, API planning, setup notes, and future feature documentation.
- `diagrams/`: Architecture diagrams, data flow diagrams, and room/device layout diagrams.

## Domain Model Plan

- Rooms:
  - Drawing Room
  - Work Room 1
  - Work Room 2
- Devices:
  - Each room has 2 fans and 3 lights.
  - Default total: 15 devices.
- Each device should track:
  - Status
  - Wattage
  - Current power
  - Room
  - Last changed timestamp
- Alerts:
  - Devices left on outside office hours should produce alerts.
  - Office hours are 9 AM to 5 PM.

## API Plan

The backend API will serve the React dashboard first and a future Discord bot later. Both clients should read the same backend data rather than duplicating state.

Planned API areas:

- Rooms
- Devices
- Live device status
- Energy usage summaries
- Office-hours alerts

## Setup Plan

The backend API and basic React frontend are now available.

Backend setup:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run migrations:

```bash
python manage.py migrate
```

Seed initial office data:

```bash
python manage.py seed_devices
```

Run the backend API:

```bash
python manage.py runserver
```

Health check:

```bash
curl http://127.0.0.1:8000/api/health/
```

Expected response:

```json
{"status":"ok"}
```

Run the device simulator in a separate terminal:

```bash
cd backend
source .venv/bin/activate
python manage.py simulate_devices
```

Run backend tests:

```bash
cd backend
source .venv/bin/activate
python manage.py test
```

Frontend setup:

```bash
cd frontend
npm install
npm run dev
```

The frontend reads from:

```text
http://127.0.0.1:8000/api
```

## Project Structure

```text
office-energy-monitor/
  backend/
  frontend/
  docs/
  diagrams/
  README.md
```
