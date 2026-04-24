from backend.game.deck import Deck
import pytest

@pytest.fixture
def basic_deck():
    return Deck()

def test_no_duplicates(basic_deck: Deck):
    for card in basic_deck.cards:
        assert basic_deck.cards.count(card) == 1

def test_deal_before_bid(basic_deck: Deck):
    hands = basic_deck.deal_before_bid()
    for hand in hands:
        assert len(hand) == 5
    
    cards_distributed = hands[0] + hands[1] + hands[2] + hands[3]
    for card in cards_distributed:
        assert cards_distributed.count(card) == 1

def test_deal_after_bid(basic_deck: Deck):
    hands = basic_deck.deal_before_bid()
    basic_deck.deal_after_bid(0, hands)
    for hand in hands:
        assert len(hand) == 8
    
    cards_distributed = hands[0] + hands[1] + hands[2] + hands[3]
    for card in cards_distributed:
        assert cards_distributed.count(card) == 1