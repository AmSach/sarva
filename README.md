# Sarva — Decentralized Compute Grid

**One repo. Backend + Frontend + Node Agent.**

## Structure
- `/main.py` — Backend API (FastAPI + PostgreSQL, deploy to Railway)
- `/frontend/` — Next.js dashboard (deploy to Vercel)
- `/agent.py` — Node agent (run on any machine)
- `/Dockerfile` — Backend container
- `/docker-compose.yml` — Local node demo

## Deploy
**Backend**: Railway — connect GitHub, set `DATABASE_URL` env var to your Neon PostgreSQL URL.
**Frontend**: Vercel — import `frontend/` as Next.js app, set `NEXT_PUBLIC_API_URL` (hardcoded in lib/api.ts already).
**Node**: `python3 agent.py` or `docker-compose up`

## Hardcoded Backend URL
`https://e65440d9-cfb0-47fa-b11a-d2070bf13013.up.railway.app`
Update in: `frontend/lib/api.ts`, `agent.py`, `Dockerfile.node`, `docker-compose.yml`

## God Mode
Any user with `user_id = "god"` gets unlimited free compute (tier = GOD).
