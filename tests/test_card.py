from backend.game.card import Card, Rank, Suit


def test_trump_jack_points():
    assert Card(Rank.JACK, Suit.HEARTS).points(Suit.HEARTS) == 20


def test_trump_nine_points():
    assert Card(Rank.NINE, Suit.HEARTS).points(Suit.HEARTS) == 14


def test_normal_ace_points():
    assert Card(Rank.ACE, Suit.SPADES).points(Suit.HEARTS) == 11


def test_normal_jack_points():
    assert Card(Rank.JACK, Suit.SPADES).points(Suit.HEARTS) == 2


def test_normal_eight_points():
    assert Card(Rank.EIGHT, Suit.DIAMONDS).points(Suit.HEARTS) == 0


def test_trump_eight_points():
    assert Card(Rank.EIGHT, Suit.HEARTS).points(Suit.HEARTS) == 0


def test_trump_jack_is_stronger_than_trump_ace():
    trump = Suit.HEARTS
    assert Card(Rank.JACK, Suit.HEARTS).strength(trump) > Card(Rank.ACE, Suit.HEARTS).strength(trump)


def test_trump_ace_is_stronger_than_normal_ace():
    trump = Suit.HEARTS
    assert Card(Rank.ACE, Suit.HEARTS).strength(trump) > Card(Rank.ACE, Suit.SPADES).strength(trump)