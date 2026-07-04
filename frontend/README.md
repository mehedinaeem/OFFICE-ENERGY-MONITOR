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

To use a deployed backend, create `frontend/.env`:

```env
VITE_API_BASE_URL=https://your-render-service.onrender.com/api
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

## Netlify Deployment

The frontend is prepared for Netlify with `netlify.toml`.

Manual Netlify settings:

```text
Base directory: frontend
Build command: npm run build
Publish directory: frontend/dist
```

Set this Netlify environment variable:

```env
VITE_API_BASE_URL=https://your-render-service.onrender.com/api
```

After Netlify deploys, add the Netlify URL to the backend `CORS_ALLOWED_ORIGINS` environment variable on Render.

## Dashboard

The dashboard polls `/api/snapshot/` every two seconds and displays:

- Summary metrics
- Estimated usage and cost
- Room cards
- Device status and manual toggle buttons
- Power breakdown bars
- Active alerts
- Simple office layout
