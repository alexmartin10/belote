from pydantic import BaseModel
from enum import Enum

from ...game.card import Rank, Suit

class GameStatus(str, Enum):
    waiting = 'waiting'
    in_progress = 'in_progress'
    over = 'over'

class GameCreate(BaseModel):
    player_name: str
    player_id: int

class GameResponse(BaseModel):
    game_id: int
    game_status: GameStatus
    players_in_game: int

class CardPlay(BaseModel):
    rank: Rank
    suit: Suit

class CardResponse(BaseModel):
    rank: Rank
    suit: Suit