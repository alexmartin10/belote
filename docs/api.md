# API documentation

The API is exposed by FastAPI. Interactive documentation is available at `/docs` when the server is running.

## System

### `GET /health`

Health check endpoint used by Render.

Response:

```json
{"status": "ok"}
```

## Games

### `POST /games/`

Creates a new solo game with one human player and three bots.

Example body:

```json
{
  "player_id": 1,
  "player_name": "Alexandre"
}
```

### `GET /games/`

Lists the games currently stored in memory.

### `GET /games/{game_id}`

Returns a summary for one game.

### `GET /games/{game_id}/status`

Returns the full current game status used by the frontend.

### `GET /games/{game_id}/hand`

Returns the human player's current hand.

### `GET /games/{game_id}/showncard`

Returns the face-up card proposed during the bidding phase.

### `POST /games/{game_id}/bid`

Submits a bid decision.

Query parameters:

- `takes`: boolean
- `suit`: optional suit, used in the second bidding round

### `POST /games/{game_id}/play`

Plays a card for the human player.

Example body:

```json
{
  "rank": "J",
  "suit": "♥"
}
```
