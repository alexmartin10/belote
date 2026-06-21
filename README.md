# 🃏 Belote Online

A personal backend project implementing the French card game **Belote** in Python, exposed through a **FastAPI** REST API and a small **React** demo interface.

The goal of this repository is to showcase backend skills: domain modeling, game-state orchestration, API design, automated testing, and deployment. The React frontend is intentionally simple and mainly exists to make the engine playable from a browser.

> Current scope: solo game against bots. The backend game engine is tested and the deployed demo is intended as a portfolio project, not as a production multiplayer platform.

---

## Live demo

The application is deployed on Render and is available here:

[Open the live demo](https://belote-z2sm.onrender.com/)

> The demo is hosted on Render's free plan. The first request may take around one minute if the service has been inactive for a while.

---

## Demo architecture

The application is deployed as a **single Render web service**:

- the Vite frontend is built during the Docker build;
- FastAPI serves the REST API;
- FastAPI also serves the built React app from `frontend/dist`;
- game sessions are stored in memory for the lifetime of the server process.

This keeps the portfolio deployment simple: one public URL, no separate frontend hosting, and no production CORS configuration required.

---

## Tech stack

| Layer | Technology |
| --- | --- |
| Game engine | Python |
| API | FastAPI |
| Dependency manager | uv |
| Tests | pytest |
| Frontend demo | React + Vite |
| Deployment | Docker on Render |

---

## Backend architecture

The backend is organized around a clear separation between the game engine and the API layer.

```text
backend/
├── api/
│   ├── main.py              # FastAPI app, CORS, health check, static frontend serving
│   ├── routers/games.py     # HTTP endpoints and in-memory game registry
│   └── schemas/game.py      # API request/response models
└── game/
    ├── game.py              # high-level orchestrator used by the API
    ├── turn.py              # one deal/round lifecycle
    ├── trick.py             # trick resolution
    ├── bid.py               # bidding state
    ├── player.py            # human/bot players and playable-card rules
    ├── deck.py              # deck and dealing
    └── card.py              # card, suit and rank model
```

`backend/game/game.py` is the orchestration layer. It coordinates the lower-level domain objects and exposes a compact interface to the API. The game engine itself does not depend on FastAPI, which makes it testable independently from HTTP.

---

## Implemented rules

- 32-card Belote deck.
- Dealing in two passes.
- Face-up card and trump proposal.
- Two bidding rounds.
- Suit-following rules.
- Trump cutting rules.
- Trump climbing rules.
- Last trick bonus.
- Contract success/failure scoring.
- Capot handling.
- Belote-rebelote bonus.
- Basic bot strategy.

---

## API overview

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/health` | Health check used by Render |
| `POST` | `/games/` | Create a new solo game |
| `GET` | `/games/` | List current in-memory games |
| `GET` | `/games/{game_id}` | Get a game summary |
| `GET` | `/games/{game_id}/status` | Get the full current game status |
| `GET` | `/games/{game_id}/hand` | Get the human player's hand |
| `GET` | `/games/{game_id}/showncard` | Get the proposed trump card |
| `POST` | `/games/{game_id}/bid` | Play a bidding decision |
| `POST` | `/games/{game_id}/play` | Play a card |

FastAPI also exposes interactive API docs at `/docs`.

---

## What this project demonstrates

This project focuses on backend engineering rather than frontend design. It demonstrates:

- modeling a real-world rules-based domain;
- separating business logic from the HTTP API layer;
- orchestrating game state through a dedicated `Game` service;
- exposing the engine through a REST API;
- validating game rules with automated tests;
- packaging and deploying a full-stack demo with Docker.

---

## Local development

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- Node.js 22+
- npm

### Install backend dependencies

```bash
uv sync
```

If you want reproducible installs, generate and commit the lockfile:

```bash
uv lock
```

### Run the backend

```bash
uv run uvicorn backend.api.main:app --reload
```

The API will be available at:

- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/docs`

### Run the frontend

In another terminal:

```bash
cd frontend
npm install
npm run dev
```

The Vite app will run on `http://localhost:5173` and will call the API at `http://127.0.0.1:8000` in development.

### Run tests

```bash
uv run pytest
```

---

## Deployment on Render

This repository is prepared for deployment as a Docker web service on Render.

### Files used by Render

- `Dockerfile` builds the React frontend and starts FastAPI.
- `render.yaml` defines the Render web service.
- `/health` is configured as the health check path.
- The server reads Render's `PORT` environment variable at runtime.

### Render setup

1. Push the repository to GitHub.
2. Create a new Render **Web Service** from the GitHub repository.
3. Choose the Docker environment, or let Render detect `render.yaml`.
4. Keep the service as a single instance / single worker because the current game state is in memory.
5. Use `/health` as the health check path.
6. After deployment, test:
   - `/health`
   - `/docs`
   - `/`

No production `VITE_API_URL` is required for the single-service deployment because the frontend calls the API on the same origin.

---

## Current limitations

The current implementation intentionally keeps the infrastructure simple for a portfolio demo.

- Game state is stored in process memory.
- Games disappear when the service restarts.
- The app should run with one worker only.
- There is no authentication.
- There is no persistence layer.
- Multiplayer is not implemented yet.
- The bot strategy is basic.

These limitations are acceptable for the current goal: demonstrating a tested backend game engine through a playable demo.

---

