"""
Tests pour valider le modèle de cartes et le deck.
Lance avec : python test_cards.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../backend/game'))

from backend.game.card import Card, Rank, Suit
from backend.game.deck import Deck


def test_card_points():
    """Vérifie les points des cartes selon l'atout."""
    trump = Suit.HEARTS

    valet_atout = Card(Rank.JACK, Suit.HEARTS)
    assert valet_atout.points(trump) == 20, "Le valet d'atout doit valoir 20 pts"

    neuf_atout = Card(Rank.NINE, Suit.HEARTS)
    assert neuf_atout.points(trump) == 14, "Le 9 d'atout doit valoir 14 pts"

    as_normal = Card(Rank.ACE, Suit.SPADES)
    assert as_normal.points(trump) == 11, "L'as hors atout doit valoir 11 pts"

    valet_normal = Card(Rank.JACK, Suit.SPADES)
    assert valet_normal.points(trump) == 2, "Le valet hors atout doit valoir 2 pts"

    print("✅ test_card_points : OK")


def test_card_strength():
    """Vérifie que le valet d'atout est bien la carte la plus forte."""
    trump = Suit.HEARTS

    valet_atout = Card(Rank.JACK, Suit.HEARTS)
    as_atout = Card(Rank.ACE, Suit.HEARTS)
    as_normal = Card(Rank.ACE, Suit.SPADES)

    assert valet_atout.strength(trump) > as_atout.strength(trump), \
        "Le valet d'atout doit être plus fort que l'as d'atout"

    assert as_atout.strength(trump) > as_normal.strength(trump), \
        "L'as d'atout doit être plus fort que l'as normal"

    print("✅ test_card_strength : OK")


def test_deck_creation():
    """Vérifie que le deck contient bien 32 cartes uniques."""
    deck = Deck()
    assert len(deck) == 32, f"Le deck doit avoir 32 cartes, il en a {len(deck)}"

    # Vérifie qu'il n'y a pas de doublons
    unique_cards = set(deck.cards)
    assert len(unique_cards) == 32, "Il ne doit pas y avoir de cartes en double"

    print("✅ test_deck_creation : OK")


def test_deck_deal():
    """Vérifie la distribution de 8 cartes à 4 joueurs."""
    deck = Deck()
    deck.shuffle()
    hands = deck.deal(num_players=4)

    assert len(hands) == 4, "Il doit y avoir 4 mains"
    for i, hand in enumerate(hands):
        assert len(hand) == 8, f"Le joueur {i} doit avoir 8 cartes, il en a {len(hand)}"

    # Vérifie qu'aucune carte n'est distribuée deux fois
    all_cards = [card for hand in hands for card in hand]
    assert len(set(all_cards)) == 32, "Chaque carte ne doit être distribuée qu'une fois"

    print("✅ test_deck_deal : OK")


def test_card_display():
    """Affiche quelques cartes pour vérification visuelle."""
    trump = Suit.HEARTS
    deck = Deck()
    deck.shuffle()
    hands = deck.deal()

    print("\n🃏 Exemple de distribution :")
    for i, hand in enumerate(hands):
        hand_str = "  ".join(str(c) for c in hand)
        total_pts = sum(c.points(trump) for c in hand)
        print(f"  Joueur {i+1} : {hand_str}  ({total_pts} pts si ♥ atout)")


if __name__ == "__main__":
    print("=== Tests du moteur de belote ===\n")
    test_card_points()
    test_card_strength()
    test_deck_creation()
    test_deck_deal()
    test_card_display()
    print("\n🎉 Tous les tests sont passés !")
