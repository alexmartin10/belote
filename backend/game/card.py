"""
Modèle d'une carte de belote.

La belote utilise 32 cartes : du 7 au As, dans 4 couleurs.
Les valeurs des cartes changent selon si elles sont à l'atout ou non.
"""

from enum import Enum


class Suit(Enum):
    """Les 4 couleurs du jeu."""
    HEARTS = "♥"    # Coeur
    DIAMONDS = "♦"  # Carreau
    CLUBS = "♣"     # Trèfle
    SPADES = "♠"    # Pique


class Rank(Enum):
    """Les 8 rangs utilisés en belote (du 7 au As)."""
    SEVEN = "7"
    EIGHT = "8"
    NINE = "9"
    TEN = "10"
    JACK = "J"
    QUEEN = "Q"
    KING = "K"
    ACE = "A"

# Points de chaque carte hors atout
POINTS_NORMAL = {
    Rank.SEVEN: 0,
    Rank.EIGHT: 0,
    Rank.NINE: 0,
    Rank.TEN: 10,
    Rank.JACK: 2,
    Rank.QUEEN: 3,
    Rank.KING: 4,
    Rank.ACE: 11,
}

# Points de chaque carte à l'atout
POINTS_TRUMP = {
    Rank.SEVEN: 0,
    Rank.EIGHT: 0,
    Rank.NINE: 14,
    Rank.TEN: 10,
    Rank.JACK: 20,   
    Rank.QUEEN: 3,
    Rank.KING: 4,
    Rank.ACE: 11,
}

# Ordre de force des cartes hors atout (pour savoir qui prend le pli)
STRENGTH_NORMAL = {
    Rank.SEVEN: 0,
    Rank.EIGHT: 1,
    Rank.NINE: 2,
    Rank.TEN: 6,
    Rank.JACK: 3,
    Rank.QUEEN: 4,
    Rank.KING: 5,
    Rank.ACE: 7,
}

# Ordre de force des cartes à l'atout
STRENGTH_TRUMP = {
    Rank.SEVEN: 0,
    Rank.EIGHT: 1,
    Rank.NINE: 6,   # Le 9 est très fort à l'atout
    Rank.TEN: 4,
    Rank.JACK: 7,   # Le valet est le plus fort à l'atout
    Rank.QUEEN: 2,
    Rank.KING: 3,
    Rank.ACE: 5,
}


class Card:
    """Représente une carte à jouer."""

    def __init__(self, rank: Rank, suit: Suit):
        self.rank = rank
        self.suit = suit

    def points(self, trump_suit: Suit) -> int:
        """Retourne la valeur en points de la carte selon l'atout."""
        if self.suit == trump_suit:
            return POINTS_TRUMP[self.rank]
        return POINTS_NORMAL[self.rank]

    def strength(self, trump_suit: Suit) -> int:
        """
        Retourne la force de la carte (pour comparer qui prend le pli).

        Les atouts ont un bonus de 100 pour être toujours au-dessus
        des cartes normales, quelle que soit leur valeur intrinsèque.
        """
        if self.is_trump(trump_suit):
            return STRENGTH_TRUMP[self.rank] + 100
        return STRENGTH_NORMAL[self.rank]

    def is_trump(self, trump_suit: Suit) -> bool:
        """Indique si la carte est un atout."""
        return self.suit == trump_suit

    def __repr__(self):
        return f"{self.rank.value}{self.suit.value}"

    def repr(self):
        return f"{self.rank.value}{self.suit.value}"
    
    def __eq__(self, other):
        return self.suit == other.suit and self.rank == other.rank