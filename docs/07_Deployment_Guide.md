# 07 Deployment Guide

## Local backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Local frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

## Docker deployment

```bash
docker compose up --build
```

## Production notes

- Replace default credentials.
- Place SQLite database and storage on persistent volumes.
- Put backend behind HTTPS reverse proxy.
- Restrict CORS to the production frontend URL.
- Back up `backend/data` and `backend/storage`.
