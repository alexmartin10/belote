# 🃏 Belote Online

A French card game (Belote) built in Python, designed to be played online in real time via a web interface.

> Personal project built to develop full stack engineering skills. The game engine is complete and fully tested. The REST API is functional. A basic React frontend (UI generated with AI assistance) allows solo play against bots.

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Game Engine | Python 3.12 |
| Backend API | FastAPI |
| Real-time | WebSockets *(coming soon)* |
| Database | PostgreSQL + SQLAlchemy *(coming soon)* |
| Frontend | React |
| Testing | pytest |

---

## Architecture

The project enforces a strict separation between the **game engine** and the **communication layer**. The engine is completely agnostic to its medium: it runs identically through a REST API or inside automated tests.

```python
# The engine receives decisions, it never asks for them
while not self._trick.is_trick_over():
    current_player = self._players[self._trick.current_player]
    self._trick.receive_card(
        current_player.index,
        current_player.play(
            self._trick.leading_player,
            self._bid.trump_suit,
            self._trick.cards_played
        )
    )
```

This design makes it trivial to plug any layer on top — a FastAPI endpoint, or a pytest test — without touching the engine at all.

---

## Rules Implemented

**Dealing**

Cards are dealt in two passes (2+3 or 3+2, chosen randomly), matching real game conventions. The face-up card determines the proposed trump suit.

**Bidding**

Two bidding rounds are handled. In the first round, players may accept the proposed trump suit. In the second round, they may name a different suit. If no one bids, the round is cancelled and a new deal begins.

**Gameplay**

Suit-following, trump cutting, and trump climbing rules are fully implemented. A player must follow the led suit if possible, cut with a trump if unable to follow, and play a higher trump if able to when cutting. If a teammate is leading the trick, the player is not forced to cut.

**Scoring**

| Card | Non-trump | Trump |
|------|-----------|-------|
| Jack | 2 pts | 20 pts |
| 9 | 0 pts | 14 pts |
| Ace | 11 pts | 11 pts |
| 10 | 10 pts | 10 pts |
| King | 4 pts | 4 pts |
| Queen | 3 pts | 3 pts |
| 8 | 0 pts | 0 pts |
| 7 | 0 pts | 0 pts |

The last trick awards 10 bonus points. The team that took the contract must score more than 81 points, otherwise the opposing team scores 162. A team that wins all 8 tricks scores 252 (capot). The King and Queen of trump held by the same player awards 20 bonus points (belote-rebelote), regardless of the contract outcome.

**Bot Strategy**

Takes the contract if the hand scores more than 50 points at the proposed trump suit. Plays the strongest available card when the team leads the trick, the weakest otherwise.

---

## Getting Started

```bash
git clone https://github.com/alexmartin10/belote.git
cd belote
pip install -r requirements.txt
```

### Run the backend

```bash
uvicorn backend.api.main:app --reload
```

### Run the frontend

```bash
cd frontend
npm install
npm run dev
```

### Run the tests

```bash
python -m pytest tests/
```

---

## Roadmap

- [x] Complete game engine
- [x] Bidding phase (2 rounds)
- [x] Gameplay rules (suit following, cutting, climbing)
- [x] Scoring and contract validation (capot, belote-rebelote)
- [x] Bot player with basic strategy
- [x] Full test suite
- [x] REST API with FastAPI
- [x] Basic React frontend (solo vs bots)
- [ ] Real-time multiplayer via WebSockets
- [ ] Authentication
- [ ] Improved bot AI
- [ ] Deployment (GCP or equivalent)