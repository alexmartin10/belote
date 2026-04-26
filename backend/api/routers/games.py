from fastapi import APIRouter, status, HTTPException

import random

from ..schemas.game import GameCreate, GameResponse, CardPlay
from ...game.game import Game
from ...game.card import Card
from ...game.player import HumanPlayer, BotPlayer, AlwaysTakingBot


games_db: dict[int, GameResponse] = {}
next_id: int = 1
games_engine: dict[int, Game] = {}
    

router = APIRouter(prefix='/games', tags=['games'])

@router.get('/', response_model=list[GameResponse])
def list_games():
    return games_db.values()

@router.get('/{game_id}')
def get_game(game_id: int):
    return get_game_or_404(game_id, games_db)

@router.post('/', response_model=GameResponse, status_code=status.HTTP_201_CREATED)
def create_game(game_create: GameCreate):
    global next_id

    game = Game(
        [
            HumanPlayer(game_create.player_id, game_create.player_name),
            BotPlayer(choose_bot_username()),
            BotPlayer(choose_bot_username()),
            AlwaysTakingBot(choose_bot_username())
        ]
    )
    game.start_game()

    games_engine[next_id] = game
    game_response = GameResponse(
        game_id=next_id,
        game_status='in_progress',
        players_in_game=1
    )
    games_db[next_id] = game_response
    next_id += 1
    return game_response

@router.post('/{game_id}/play')
def play(game_id: int, card_play: CardPlay):
    game: Game = get_game_or_404(game_id, games_engine)
    card = Card(card_play.rank, card_play.suit)
    try:
        game.play_card(card)
    except ValueError as e:
        raise HTTPException(400, str(e))
    return game.get_status()

def get_game_or_404(game_id: int, db: dict[int: Game | GameResponse]) -> Game | GameResponse:
    response = db.get(game_id)
    if response is not None:
        return response
    else:
        raise HTTPException(status_code=404, detail='No game with this id.')
    
def choose_bot_username():
    names = ['Paul', 'Pierre', 'Jean', 'Luc', 'Marc', 'Matthieu']
    return random.choice(names)

def count_human_players_in_game(game):
    """for the future to put in GameResponse"""
    raise NotImplementedError