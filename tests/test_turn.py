from backend.game.turn import Turn
from backend.game.player import BotPlayer, AlwaysTakingBot
from backend.game.deck import Deck
import pytest

@pytest.fixture
def basic_turn():
    players = {i: BotPlayer(i, f'Bot{i}') for i in range(4)}
    players[0] = AlwaysTakingBot(0, 'Taker')
    for player in players.values():
        player.set_player_index(player.id)
    turn = Turn(players, 0, Deck())
    return turn

def test_turn_without_crash(basic_turn: Turn):
    points = basic_turn.main()

    assert points is not None

def test_turn_finished(basic_turn: Turn):
    _ = basic_turn.main()

    assert basic_turn.is_turn_over() == True

def test_turn_is_played_or_aborted(basic_turn: Turn):
    _ = basic_turn.main()
    assert basic_turn.turn_finished == True or basic_turn.turn_aborted == True

def test_total_points_is_162(basic_turn: Turn):
    points = basic_turn.main()
    if basic_turn.turn_aborted is not None:
        assert sum(points.values()) == 162