from backend.game.bid import Bid
from backend.game.card import Card, Rank, Suit

import pytest

def test_first_round_taker():
    trump_card = Card(Rank.TEN, Suit.HEARTS)
    order = [2, 3, 0, 1]
    bid = Bid(order=order, trump_card=trump_card)

    bid.receive_bid(2, False)
    bid.receive_bid(3, False)
    bid.receive_bid(0, True)

    assert bid.taker == 0

def test_second_round_taker():
    trump_card = Card(Rank.TEN, Suit.HEARTS)
    order = [1, 2, 3, 0]
    bid = Bid(order=order, trump_card=trump_card)

    bid.receive_bid(1, False)
    bid.receive_bid(2, False)
    bid.receive_bid(3, False)
    bid.receive_bid(0, False)

    assert bid.current_bidder == 1
    assert bid.round == 2
    assert bid.taker == None
    assert bid.is_bidding_over() == False

    bid.receive_bid(1, True, Suit.DIAMONDS)

    assert bid.taker == 1
    assert bid.trump_suit == Suit.DIAMONDS

def test_wrong_player_raises_error():
    trump_card = Card(Rank.TEN, Suit.HEARTS)
    order = [2, 3, 0, 1]
    bid = Bid(order=order, trump_card=trump_card)

    with pytest.raises(ValueError):
        bid.receive_bid(0, True)

def test_no_taker_in_two_rounds():
    trump_card = Card(Rank.TEN, Suit.HEARTS)
    order = [1, 2, 3, 0]
    bid = Bid(order=order, trump_card=trump_card)

    bid.receive_bid(1, False)
    bid.receive_bid(2, False)
    bid.receive_bid(3, False)
    bid.receive_bid(0, False)

    bid.receive_bid(1, False)
    bid.receive_bid(2, False)
    bid.receive_bid(3, False)
    bid.receive_bid(0, False)

    assert bid.current_bidder == None
    assert bid.taker == None
    assert bid.is_bidding_over() == True

