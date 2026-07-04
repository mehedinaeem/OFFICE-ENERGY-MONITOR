# Office Energy Monitor

Office Energy Monitor is a hackathon project for monitoring office lights, fans, power usage, and alerts from one backend API. The current version uses simulated data only, so it can be demoed without real hardware.

## Project Overview

The system models a small office with three rooms:

- Drawing Room
- Work Room 1
- Work Room 2

Each room has two fans and three lights. The backend stores every room, device, status change, power value, and alert. The React dashboard reads from the backend and updates live through polling.

## Problem Statement

Small offices often leave lights and fans running after work hours because there is no central visibility into room-level device usage. This wastes electricity and makes it difficult for office admins or facilities teams to quickly understand which areas need attention.

Office Energy Monitor solves this demo problem by giving a live operational dashboard, basic alerting, estimated usage calculations, and API endpoints that can later be used by a Discord bot or hardware devices.

## Architecture

```text
Simulated devices / future hardware
          |
          v
Django + DRF backend API  <--- future Discord bot
          |
          v
React + Vite dashboard
```

The backend is the single source of truth. The simulator, dashboard, manual toggles, and future Discord bot all read from or write to the same database through Django models and API endpoints.

## Tech Stack

- Backend: Django, Django REST Framework
- Frontend: React, Vite
- API client: Axios
- Database: SQLite for local demo
- Styling: Plain CSS
- Data source: Dummy seeded data and a random simulator

## Features Completed

- Django backend project and `monitor` app
- Room, Device, and Alert models
- Seed command for default office rooms and devices
- Simulator command to randomly toggle devices
- Manual device toggle API
- REST API for dashboard and future bot usage
- Live React dashboard with 2-second polling
- Summary cards, room cards, power breakdown, alerts, and simple office layout
- Estimated hourly usage, office-day usage, and daily cost
- Bot-friendly API response for status summaries
- Basic backend tests

## Backend Setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_devices
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

Run backend tests:

```bash
cd backend
source .venv/bin/activate
python manage.py test
```

## Frontend Setup

In a separate terminal:

```bash
cd frontend
npm install
npm run dev
```

The frontend expects the backend API at:

```text
http://127.0.0.1:8000/api
```

## Simulator Command

Run the simulator in a separate backend terminal:

```bash
cd backend
source .venv/bin/activate
python manage.py simulate_devices
```

The simulator randomly selects one or two devices every five seconds and toggles them using the same `Device.set_status()` method used by manual controls.

## API Endpoints

Core:

- `GET /api/health/`
- `GET /api/snapshot/`
- `GET /api/devices/`
- `POST /api/devices/<id>/toggle/`
- `GET /api/rooms/<slug>/`
- `GET /api/usage/`
- `GET /api/alerts/`

Bot-friendly:

- `GET /api/status-summary/`

## Dashboard Explanation

The dashboard polls `/api/snapshot/` every two seconds. It shows:

- Total rooms
- Total devices
- Devices currently ON
- Current power usage
- Active alerts
- Estimated hourly usage
- Estimated office-day usage based on eight hours
- Estimated daily cost in BDT
- Room-level device state
- Room-wise power bars
- Active alert cards
- Simple top-view office layout

Each device row includes a manual Toggle button for demo control.

## Dummy Data Explanation

The current system does not connect to real hardware. Dummy data is created by:

```bash
python manage.py seed_devices
```

This creates:

- 3 rooms
- 15 devices total
- 2 fans and 3 lights per room
- Fan wattage: 60W
- Light wattage: 15W

The simulator and manual toggle controls update this same SQLite database.

## Alert Logic

Office hours are treated as 9 AM to 5 PM.

Alerts are generated when `/api/snapshot/` is requested:

- If current local time is outside office hours and a room has devices ON, a warning alert is created for that room.
- If total power is above 400W, a danger alert is created.
- For the MVP, unresolved alerts are cleared and recreated from the current state on each snapshot request.

## Usage Estimate Logic

Usage and cost values are demo estimates only:

- Estimated hourly kWh = `total_power / 1000`
- Estimated office-day kWh = `estimated_hourly_kwh * 8`
- Estimated daily cost = `estimated_daily_kwh * 10`

The assumed demo rate is 10 BDT/kWh.

## Future Wokwi Hardware Plan

The next hardware step is to simulate physical devices in Wokwi using an ESP32-style setup. The Wokwi simulation can later send device status or sensor data to the Django backend API.

Planned hardware flow:

```text
Wokwi simulated sensors/devices -> Django API -> React dashboard + Discord bot
```

Possible future hardware inputs:

- Light switch state
- Fan switch state
- Room occupancy signal
- Power sensor readings

## Future Discord Bot Plan

The Discord bot will read from the same backend API as the dashboard.

Planned commands:

```text
!status
!room work1
!usage
!alerts
```

Planned API mapping:

- `!status` -> `GET /api/status-summary/`
- `!room work1` -> `GET /api/rooms/work1/`
- `!usage` -> `GET /api/usage/`
- `!alerts` -> `GET /api/alerts/`

## Project Structure

```text
office-energy-monitor/
  backend/
  frontend/
  docs/
  diagrams/
  README.md
```
