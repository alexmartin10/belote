from backend.game.bid import Bid
from backend.game.card import Card, Rank, Suit
import pytest


@pytest.fixture
def basic_bid():
    """A Bid starting with order [2, 3, 0, 1] and 10 of Hearts as trump card."""
    return Bid(order=[1, 2, 3, 0], trump_card=Card(Rank.TEN, Suit.HEARTS))


def test_first_round_taker(basic_bid: Bid):
    basic_bid.receive_bid(1, False)
    basic_bid.receive_bid(2, False)
    basic_bid.receive_bid(3, True)
    assert basic_bid.taker == 3


def test_second_round_starts_after_all_pass(basic_bid: Bid):
    basic_bid.receive_bid(1, False)
    basic_bid.receive_bid(2, False)
    basic_bid.receive_bid(3, False)
    basic_bid.receive_bid(0, False)

    assert basic_bid.current_bidder == 1
    assert basic_bid.round == 2
    assert basic_bid.taker is None
    assert basic_bid.is_bidding_over() is False


def test_second_round_taker(basic_bid: Bid):
    basic_bid.receive_bid(1, False)
    basic_bid.receive_bid(2, False)
    basic_bid.receive_bid(3, False)
    basic_bid.receive_bid(0, False)
    basic_bid.receive_bid(1, True, Suit.DIAMONDS)

    assert basic_bid.taker == 1
    assert basic_bid.trump_suit == Suit.DIAMONDS


def test_out_of_turn_bid_raises_error(basic_bid: Bid):
    with pytest.raises(ValueError):
        basic_bid.receive_bid(0, True)


def test_no_taker_after_two_rounds(basic_bid: Bid):
    for player in [1, 2, 3, 0, 1, 2, 3, 0]:
        basic_bid.receive_bid(player, False)

    assert basic_bid.current_bidder is None
    assert basic_bid.taker is None
    assert basic_bid.is_bidding_over() is True