from backend.game.turn import Turn
from backend.game.player import BotPlayer, AlwaysTakingBot
from backend.game.deck import Deck
import pytest


@pytest.fixture
def basic_turn():
    """A Turn with player 0 as AlwaysTakingBot to guarantee a taker exists."""
    players = {i: BotPlayer(i, f'bot{i}') for i in range(4)}
    players[0] = AlwaysTakingBot(0, 'taker')
    for player in players.values():
        player.set_player_index(player.id)
    return Turn(players, 0, Deck())


def test_turn_returns_points(basic_turn: Turn):
    assert basic_turn.main() is not None


def test_turn_is_over_after_main(basic_turn: Turn):
    basic_turn.main()
    assert basic_turn.is_turn_over() is True


def test_turn_is_finished_or_aborted(basic_turn: Turn):
    basic_turn.main()
    assert basic_turn.turn_finished is True or basic_turn.turn_aborted is True


def test_total_points_is_162(basic_turn: Turn):
    points = basic_turn.main()
    if not basic_turn.turn_aborted:
        assert sum(points.values()) == 162