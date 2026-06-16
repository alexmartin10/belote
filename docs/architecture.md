# Backend architecture

The backend is intentionally separated into two layers:

1. **Domain/game engine** in `backend/game/`.
2. **HTTP/API layer** in `backend/api/`.

The API creates and stores `Game` instances, but the rules of Belote live outside the API layer.

## Main flow

```text
HTTP request
   ↓
FastAPI router: backend/api/routers/games.py
   ↓
Game orchestrator: backend/game/game.py
   ↓
Turn / Bid / Trick / Player / Deck / Card
   ↓
Game status returned to API
```

## Key classes

| Class | Role |
| --- | --- |
| `Game` | High-level orchestration used by the API |
| `Turn` | Handles one round/deal lifecycle |
| `Bid` | Tracks bidding phase and trump selection |
| `Trick` | Tracks cards played in a trick and determines the winner |
| `Player` | Holds player hand and play/bid behavior |
| `HumanPlayer` | Receives decisions through the API |
| `BotPlayer` | Plays automatically with a simple strategy |
| `Deck` | Builds and deals the 32-card deck |
| `Card` | Represents rank/suit and scoring behavior |

## Current state management

`backend/api/routers/games.py` stores active games in module-level dictionaries:

```python
games_db = {}
games_engine = {}
next_id = 1
```

This is simple and useful for a demo, but it is not persistent. A production version should move this state to a database or a shared in-memory store.

## Why this design is useful

The game engine does not import FastAPI. This means it can be tested directly with pytest and reused later behind another interface, such as WebSockets or a CLI.
