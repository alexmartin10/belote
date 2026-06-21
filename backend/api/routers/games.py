"""HTTP routes for creating and playing Belote games.

The router keeps a small in-memory registry of games. This is acceptable for
the portfolio demo deployment, but it means games are lost when the process
restarts and the app should run with a single worker.
"""

import random

from fastapi import APIRouter, HTTPException, status

from ..schemas.game import CardPlay, CardResponse, GameCreate, GameResponse, GameStatus
from ...game.card import Card, Suit
from ...game.game import Game
from ...game.player import BotPlayer, HumanPlayer


games_db: dict[int, GameResponse] = {}
next_id: int = 1
games_engine: dict[int, Game] = {}

router = APIRouter(prefix="/games", tags=["games"])


@router.get("/", response_model=list[GameResponse])
def list_games() -> list[GameResponse]:
    """Return all games currently tracked in memory.

    Returns:
        A list of lightweight game summaries.
    """
    return list(games_db.values())


@router.get("/{game_id}")
def get_game(game_id: int) -> GameResponse:
    """Return the summary for a single game.

    Args:
        game_id: Identifier of the game to retrieve.

    Returns:
        The matching game summary.

    Raises:
        HTTPException: If no game exists with the provided id.
    """
    return get_game_or_404(game_id, games_db)


@router.post("/", response_model=GameResponse, status_code=status.HTTP_201_CREATED)
def create_game(game_create: GameCreate) -> GameResponse:
    """Create a new solo game with one human player and three bots.

    The game engine is initialized immediately and bidding starts until the
    first human decision is required. The game is then stored in the in-memory
    registry used by this demo API.

    Args:
        game_create: Payload containing the human player's id and display name.

    Returns:
        A lightweight summary of the newly created game.
    """
    global next_id

    game = Game(
        [
            HumanPlayer(game_create.player_id, game_create.player_name),
            BotPlayer(choose_bot_username()),
            BotPlayer(choose_bot_username()),
            BotPlayer(choose_bot_username()),
        ]
    )
    game.start_game()

    games_engine[next_id] = game
    game_response = GameResponse(
        game_id=next_id,
        game_status=GameStatus.in_progress,
        players_in_game=1,
    )
    games_db[next_id] = game_response
    next_id += 1
    return game_response


@router.post("/{game_id}/play")
def play(game_id: int, card_play: CardPlay) -> dict:
    """Play one card for the human player in the selected game.

    Args:
        game_id: Identifier of the game to update.
        card_play: Rank and suit of the card selected by the frontend.

    Returns:
        The updated game status after the human move and any automatic bot moves.

    Raises:
        HTTPException: If the game does not exist or the card is illegal.
    """
    game: Game = get_game_or_404(game_id, games_engine)
    card = Card(card_play.rank, card_play.suit)
    try:
        game.play_card(card)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    if game.get_status()["game_over"]:
        games_db[game_id].game_status = GameStatus.over

    return game.get_status()


@router.post("/{game_id}/bid")
def bid(game_id: int, takes: bool, suit: Suit = None) -> dict:
    """Submit the human player's bidding decision.

    Args:
        game_id: Identifier of the game to update.
        takes: True if the human accepts the contract, False to pass.
        suit: Trump suit chosen during the second bidding round, if applicable.

    Returns:
        The updated game status after the human bid and any automatic bot bids.

    Raises:
        HTTPException: If the game does not exist or the bid is illegal.
    """
    game: Game = get_game_or_404(game_id, games_engine)
    try:
        game.play_bid(takes, suit)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    return game.get_status()


@router.get("/{game_id}/hand", response_model=list[CardResponse])
def get_player_hand(game_id: int) -> list[Card]:
    """Return the human player's current hand.

    Args:
        game_id: Identifier of the game to inspect.

    Returns:
        The list of cards currently held by the human player.

    Raises:
        HTTPException: If no game exists with the provided id.
    """
    game: Game = get_game_or_404(game_id, games_engine)
    human_index = game.get_human_player_index()
    return game.get_player_hand(human_index)


@router.get("/{game_id}/showncard", response_model=CardResponse)
def get_card_shown(game_id: int) -> Card:
    """Return the face-up card proposed during the bidding phase.

    Args:
        game_id: Identifier of the game to inspect.

    Returns:
        The card used to propose the initial trump suit.

    Raises:
        HTTPException: If no game exists with the provided id.
    """
    game: Game = get_game_or_404(game_id, games_engine)
    return game.get_status()["card_shown"]


@router.get("/{game_id}/status")
def get_status(game_id: int) -> dict:
    """Return a complete status snapshot for a game.

    Args:
        game_id: Identifier of the game to inspect.

    Returns:
        A dictionary describing scores, bidding state, trick state, and game-over status.

    Raises:
        HTTPException: If no game exists with the provided id.
    """
    game: Game = get_game_or_404(game_id, games_engine)
    return game.get_status()


def get_game_or_404(game_id: int, db: dict[int, Game | GameResponse]) -> Game | GameResponse:
    """Return a game object from a registry or raise a 404 error.

    Args:
        game_id: Identifier to look up.
        db: Registry mapping game ids to either engine objects or response models.

    Returns:
        The object stored for the given id.

    Raises:
        HTTPException: If the id is not present in the registry.
    """
    response = db.get(game_id)
    if response is not None:
        return response

    raise HTTPException(status_code=404, detail="No game with this id.")


def choose_bot_username() -> str:
    """Choose a display name for a bot player.

    Returns:
        A random first name from the demo bot-name pool.
    """
    names = ["Paul", "Pierre", "Jean", "Luc", "Marc", "Matthieu"]
    return random.choice(names)


def count_human_players_in_game(game: Game) -> int:
    """Placeholder for future multiplayer game summaries.

    Args:
        game: Game engine instance to inspect.

    Raises:
        NotImplementedError: Always, because the current demo only supports one human.
    """
    raise NotImplementedError
