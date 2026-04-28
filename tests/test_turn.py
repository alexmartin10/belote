from backend.game.turn import Turn
from backend.game.player import BotPlayer, AlwaysTakingBot, Player
from backend.game.deck import Deck
import pytest



def turn_simulation():
    """A Turn with player 0 as AlwaysTakingBot to guarantee a taker exists."""
    players = {i: BotPlayer(f'bot{i}') for i in range(4)}
    players[0] = AlwaysTakingBot('taker')
    for i in players.keys():
        players[i].set_player_index(i)
    turn =  Turn(players, 0, Deck())
    turn.deal()
    while not turn.is_turn_over():
        status = turn.get_status()
        player_index = status['current_player']
        player = players[player_index]
        turn.play_one_card(
            player.index,
            player.play(
                status['leading_player'],
                status['trump_suit'],
                status['cards_played']
            )
        )
    return turn

turn = turn_simulation()

def test_turn_is_over_after_main():
    assert turn.is_turn_over() is True


def test_total_points_is_162():
    if not turn.turn_aborted:
        assert sum(turn.points.values()) == 162