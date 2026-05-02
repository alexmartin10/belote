# 🃏 Belote Online

A French card game (Belote) built in Python, designed to be played online in real time via a web interface.

> Personal project built to develop full stack engineering skills. The game engine is complete and fully tested. The API and frontend are under development.

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Game Engine | Python 3.12 |
| Backend API | FastAPI |
| Real-time | WebSockets *(coming soon)* |
| Database | PostgreSQL + SQLAlchemy *(coming soon)* |
| Frontend | React *(coming soon)* |
| Testing | pytest |

---

## Architecture

The project enforces a strict separation between the **game engine** and the **communication layer**. The engine is completely agnostic to its medium: it runs identically on a terminal, through a REST API, or inside automated tests.

```
belote/
├── backend/
│   └── game/
│       ├── card.py       # Card model, points and strength based on trump suit
│       ├── deck.py       # 32-card deck, dealing logic
│       ├── bid.py        # Bidding phase (2 rounds)
│       ├── fold.py       # Single trick logic
│       ├── player.py     # Human players and bots
│       ├── turn.py       # Full round orchestration
│       └── game.py       # Full game orchestration
└── tests/
    ├── test_card.py
    ├── test_deck.py
    ├── test_bid.py
    ├── test_fold.py
    ├── test_player.py
    └── test_turn.py
```

### Game Engine Design

The engine operates as a **state machine**. Each class exposes methods to advance the state (`receive_bid`, `receive_card`) and methods to query it (`is_bidding_over`, `is_fold_over`). No class inside the engine ever blocks waiting for user input.

```python
# The engine receives decisions, it never asks for them
while not self.bid.is_bidding_over():
    current_player = self.players[self.bid.current_bidder]
    self.bid.receive_bid(
        current_player.index,
        current_player.decide_bid(self.bid.trump_card)
    )
```

This design makes it trivial to plug any layer on top: a terminal `input()`, a FastAPI endpoint, or a pytest test, without touching the engine at all.

---

## Rules Implemented

**Dealing**

Cards are dealt in two passes (2+3 or 3+2, chosen randomly), matching real game conventions. The face-up card determines the proposed trump suit.

**Bidding**

Two bidding rounds are handled. In the first round, players may accept the proposed trump suit. In the second round, they may name a different suit. If no one bids, the round is cancelled and a new deal begins.

**Gameplay**

Suit-following, trump cutting, and trump climbing rules are fully implemented. A player must follow the led suit if possible, cut with a trump if unable to follow, and play a higher trump if able to when cutting.

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

The last trick awards 10 bonus points. The team that took the contract must score more than 81 points, otherwise the opposing team scores 162.

---

## Getting Started

```bash
git clone https://github.com/your-username/belote.git
cd belote
pip install -r requirements.txt
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
- [x] Scoring and contract validation
- [x] Bot player (basic strategy)
- [x] Full test suite
- [ ] REST API with FastAPI
- [ ] Real-time multiplayer via WebSockets
- [ ] Authentication
- [ ] React frontend
- [ ] Deployment

---

## Contributing

The project is under active development. Contributions are welcome, especially on AI strategy and the frontend.
