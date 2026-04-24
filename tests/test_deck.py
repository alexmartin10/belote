from backend.game.deck import Deck
import pytest


@pytest.fixture
def basic_deck():
    """A fresh 32-card deck."""
    return Deck()


def test_deck_has_no_duplicates(basic_deck: Deck):
    for card in basic_deck.cards:
        assert basic_deck.cards.count(card) == 1


def test_deal_before_bid_gives_five_cards_per_player(basic_deck: Deck):
    hands = basic_deck.deal_before_bid()
    for hand in hands:
        assert len(hand) == 5


def test_deal_before_bid_has_no_duplicates(basic_deck: Deck):
    hands = basic_deck.deal_before_bid()
    all_cards = hands[0] + hands[1] + hands[2] + hands[3]
    for card in all_cards:
        assert all_cards.count(card) == 1


def test_deal_after_bid_gives_eight_cards_per_player(basic_deck: Deck):
    hands = basic_deck.deal_before_bid()
    basic_deck.deal_after_bid(0, hands)
    for hand in hands:
        assert len(hand) == 8


def test_deal_after_bid_has_no_duplicates(basic_deck: Deck):
    hands = basic_deck.deal_before_bid()
    basic_deck.deal_after_bid(0, hands)
    all_cards = hands[0] + hands[1] + hands[2] + hands[3]
    for card in all_cards:
        assert all_cards.count(card) == 1