# Deployment guide — Render

This project is designed to be deployed on Render as a single Docker web service.

## Why a single service?

The backend currently stores game sessions in process memory. A single-service deployment keeps the architecture simple and reliable for a portfolio demo:

- one public URL;
- no separate frontend hosting;
- no production CORS issue;
- no external database required;
- no cross-service API URL to maintain.

The tradeoff is that game sessions are temporary and disappear when the Render service restarts.

## Required files

| File | Purpose |
| --- | --- |
| `Dockerfile` | Builds the frontend, installs backend dependencies with `uv`, starts FastAPI |
| `pyproject.toml` | Python dependencies and development dependencies |
| `render.yaml` | Render web service declaration |
| `.dockerignore` | Keeps the Docker build context clean |
| `backend/api/main.py` | Serves API routes, health check, and built frontend |

## Important deployment details

Render exposes the HTTP port through the `PORT` environment variable. The Docker command uses it automatically:

```bash
uv run uvicorn backend.api.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1
```

The `--workers 1` part is intentional. The app stores game engines in memory, so multiple workers would each have their own isolated game registry.

## Steps

1. Commit the project to GitHub.
2. Make sure `.venv/`, `node_modules/`, `frontend/dist/`, `__pycache__/`, and `.env` are not committed.
3. Commit `pyproject.toml`.
4. If you already have a local `uv.lock`, commit it too. If not, run:

```bash
uv lock
```

5. Go to Render and create a new Web Service from the repository.
6. Select Docker deployment.
7. Set health check path to:

```text
/health
```

8. Deploy.
9. Validate the deployment:

```text
https://your-service.onrender.com/health
https://your-service.onrender.com/docs
https://your-service.onrender.com/
```

## Environment variables

For the recommended single-service Render deployment, no production `VITE_API_URL` is needed.

For local development with Vite and FastAPI running separately:

```bash
VITE_API_URL=http://127.0.0.1:8000
CORS_ALLOWED_ORIGINS=http://localhost:5173
```

For a split deployment later, set:

```bash
VITE_API_URL=https://your-backend-url
CORS_ALLOWED_ORIGINS=https://your-frontend-url
```

## Troubleshooting

### The frontend loads but API calls fail

Check whether `VITE_API_URL` was set incorrectly at build time. For the single-service deployment, it should usually be empty.

### Render says the service is unhealthy

Open `/health`. It must return:

```json
{"status": "ok"}
```

### Games randomly disappear

This is expected if the Render instance restarts or sleeps. The current app has no database.

### A game works locally but not after scaling

Do not use multiple workers or multiple instances until game state is moved to a shared store such as Redis or PostgreSQL.
