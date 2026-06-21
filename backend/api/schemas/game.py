"""Pydantic models used by the games API routes."""

from enum import Enum

from pydantic import BaseModel

from ...game.card import Rank, Suit


class GameStatus(str, Enum):
    """Possible lifecycle states for a game exposed by the API."""

    waiting = "waiting"
    in_progress = "in_progress"
    over = "over"


class GameCreate(BaseModel):
    """Request payload used to create a solo Belote game.

    Attributes:
        player_name: Display name of the human player.
        player_id: External identifier for the human player.
    """

    player_name: str
    player_id: int


class GameResponse(BaseModel):
    """Lightweight game summary returned by list and create endpoints.

    Attributes:
        game_id: In-memory identifier assigned by the API.
        game_status: Current lifecycle state of the game.
        players_in_game: Number of human players currently represented in the game.
    """

    game_id: int
    game_status: GameStatus
    players_in_game: int


class CardPlay(BaseModel):
    """Request payload representing a card selected by the frontend.

    Attributes:
        rank: Rank of the card to play.
        suit: Suit of the card to play.
    """

    rank: Rank
    suit: Suit


class CardResponse(BaseModel):
    """Response model representing a card sent to the frontend.

    Attributes:
        rank: Rank of the card.
        suit: Suit of the card.
    """

    rank: Rank
    suit: Suit
