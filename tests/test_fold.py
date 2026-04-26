from backend.game.trick import Trick
from backend.game.player import BotPlayer
from backend.game.card import Card, Rank, Suit
import pytest


@pytest.fixture
def basic_trick():
    """A Trick with Hearts as trump, starting player 1.

    Hands:
        Player 0: 10♠, A♣, 7♥
        Player 1: J♥, K♦, 8♣
        Player 2: 9♥, Q♦, 10♣
        Player 3: 10♥, A♦, 9♣
    """
    players = {i: BotPlayer(i, f"bot{i}") for i in range(4)}
    players[0].make_hand([Card(Rank.TEN, Suit.SPADES), Card(Rank.ACE, Suit.CLUBS), Card(Rank.SEVEN, Suit.HEARTS)])
    players[1].make_hand([Card(Rank.JACK, Suit.HEARTS), Card(Rank.KING, Suit.DIAMONDS), Card(Rank.EIGHT, Suit.CLUBS)])
    players[2].make_hand([Card(Rank.NINE, Suit.HEARTS), Card(Rank.QUEEN, Suit.DIAMONDS), Card(Rank.TEN, Suit.CLUBS)])
    players[3].make_hand([Card(Rank.TEN, Suit.HEARTS), Card(Rank.ACE, Suit.DIAMONDS), Card(Rank.NINE, Suit.CLUBS)])
    return Trick(players, 1, Suit.HEARTS)


def test_out_of_turn_card_raises_error(basic_trick: Trick):
    with pytest.raises(ValueError):
        basic_trick.receive_card(2, Card(Rank.NINE, Suit.HEARTS))


def test_trump_jack_wins_trick(basic_trick: Trick):
    basic_trick.receive_card(1, Card(Rank.JACK, Suit.HEARTS))
    basic_trick.receive_card(2, Card(Rank.NINE, Suit.HEARTS))
    basic_trick.receive_card(3, Card(Rank.TEN, Suit.HEARTS))
    basic_trick.receive_card(0, Card(Rank.SEVEN, Suit.HEARTS))

    assert basic_trick.is_trick_over() is True
    assert basic_trick.leading_player == 1
    assert basic_trick.points == 44


def test_highest_normal_card_wins_trick(basic_trick: Trick):
    basic_trick.receive_card(1, Card(Rank.EIGHT, Suit.CLUBS))
    basic_trick.receive_card(2, Card(Rank.TEN, Suit.CLUBS))
    basic_trick.receive_card(3, Card(Rank.NINE, Suit.CLUBS))
    basic_trick.receive_card(0, Card(Rank.ACE, Suit.CLUBS))

    assert basic_trick.is_trick_over() is True
    assert basic_trick.leading_player == 0
    assert basic_trick.points == 21


def test_trump_wins_over_normal_ace(basic_trick: Trick):
    basic_trick.receive_card(1, Card(Rank.KING, Suit.DIAMONDS))
    basic_trick.receive_card(2, Card(Rank.QUEEN, Suit.DIAMONDS))
    basic_trick.receive_card(3, Card(Rank.ACE, Suit.DIAMONDS))
    basic_trick.receive_card(0, Card(Rank.SEVEN, Suit.HEARTS))

    assert basic_trick.is_trick_over() is True
    assert basic_trick.leading_player == 0
    assert basic_trick.points == 18