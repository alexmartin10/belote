from backend.game.card import Card, Rank, Suit

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

    huit_normal = Card(Rank.EIGHT, Suit.DIAMONDS)
    assert huit_normal.points(trump) == 0, "Huit normal vaut 0 points"

    huit_atout = Card(Rank.EIGHT, Suit.HEARTS)
    assert huit_atout.points(trump) == 0, "Huit atout vaut 0 points"


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
