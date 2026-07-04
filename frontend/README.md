# Office Energy Monitor Frontend

React + Vite dashboard for the Office Energy Monitor project.

## Setup

```bash
npm install
npm run dev
```

The dashboard expects the backend to be running at:

```text
http://127.0.0.1:8000/api
```

## Scripts

Run development server:

```bash
npm run dev
```

Run lint:

```bash
npm run lint
```

Build production assets:

```bash
npm run build
```

## Dashboard

The dashboard polls `/api/snapshot/` every two seconds and displays:

- Summary metrics
- Estimated usage and cost
- Room cards
- Device status and manual toggle buttons
- Power breakdown bars
- Active alerts
- Simple office layout
