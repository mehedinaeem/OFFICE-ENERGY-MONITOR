# 3-Minute Demo Script

## 0:00-0:30 Problem Intro

Small offices often waste electricity because lights and fans are left on after office hours. Office admins usually do not have a quick room-by-room view of what is currently running.

Office Energy Monitor gives a simple live dashboard for rooms, devices, power usage, and alerts.

## 0:30-1:00 Architecture Explanation

The backend is Django with Django REST Framework. It is the single source of truth for rooms, devices, power, and alerts.

The frontend is React with Vite. It polls the backend every two seconds and displays the live office state.

For now, data is simulated. Later, Wokwi hardware simulation and a Discord bot can read from the same backend API.

## 1:00-1:45 Dashboard Live Demo

Open the dashboard and show the main sections:

- Summary cards for rooms, devices, devices ON, power, alerts, and estimates
- Room status cards for Drawing Room, Work Room 1, and Work Room 2
- Room-wise power breakdown
- Active alerts
- Office layout with light and fan indicators

Explain that every value comes from the backend API.

## 1:45-2:15 Simulator and Manual Toggle

Show the simulator command:

```bash
python manage.py simulate_devices
```

Explain that it randomly toggles devices every five seconds.

Then use the dashboard Toggle button on a device. The dashboard refreshes immediately because it calls the backend toggle API and then reloads the snapshot.

## 2:15-2:40 Alert Demo

Explain the alert logic:

- Office hours are 9 AM to 5 PM.
- Devices left ON outside office hours create warning alerts.
- Total power above 400W creates a danger alert.

Show the alert cards or explain how they appear when the condition is met.

## 2:40-3:00 Future Plan

Next, Wokwi can simulate real hardware inputs such as switches, occupancy, or power sensors. Those devices would send data to the same Django API.

A Discord bot can also be added later using the bot-friendly API endpoints:

- `!status`
- `!room work1`
- `!usage`
- `!alerts`

The important point is that the dashboard, future hardware, and Discord bot all share one backend source of truth.
