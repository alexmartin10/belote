"""Belote card model.

Belote uses 32 cards: from 7 to Ace, in 4 suits.
Card point values and strengths change depending on whether they are trump or not.
"""

from enum import Enum


class Suit(Enum):
    """The 4 suits in the game."""
    HEARTS = "♥"
    DIAMONDS = "♦"
    CLUBS = "♣"
    SPADES = "♠"


class Rank(Enum):
    """The 8 ranks used in Belote (7 through Ace)."""
    SEVEN = "7"
    EIGHT = "8"
    NINE = "9"
    TEN = "10"
    JACK = "J"
    QUEEN = "Q"
    KING = "K"
    ACE = "A"


# Point value of each card when not trump
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

# Point value of each card when trump
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

# Relative strength of each card when not trump (used to determine trick winner)
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

# Relative strength of each card when trump
STRENGTH_TRUMP = {
    Rank.SEVEN: 0,
    Rank.EIGHT: 1,
    Rank.NINE: 6,   # The 9 is very strong as trump
    Rank.TEN: 4,
    Rank.JACK: 7,   # The Jack is the strongest trump card
    Rank.QUEEN: 2,
    Rank.KING: 3,
    Rank.ACE: 5,
}


class Card:
    """A single playing card.

    Attributes:
        rank: The rank of the card (7 through Ace).
        suit: The suit of the card (Hearts, Diamonds, Clubs, Spades).
    """

    def __init__(self, rank: Rank, suit: Suit):
        """Initializes a Card with a rank and a suit.

        Args:
            rank: The rank of the card.
            suit: The suit of the card.
        """
        self.rank = rank
        self.suit = suit

    def points(self, trump_suit: Suit) -> int:
        """Returns the point value of the card given the trump suit.

        Args:
            trump_suit: The current trump suit.

        Returns:
            The point value of the card.
        """
        if self.suit == trump_suit:
            return POINTS_TRUMP[self.rank]
        return POINTS_NORMAL[self.rank]

    def strength(self, trump_suit: Suit) -> int:
        """Returns the strength of the card used to determine trick winners.

        Trump cards receive a +100 bonus to always outrank non-trump cards,
        regardless of their intrinsic strength value.

        Args:
            trump_suit: The current trump suit.

        Returns:
            An integer representing the card's strength.
        """
        if self.is_trump(trump_suit):
            return STRENGTH_TRUMP[self.rank] + 100
        return STRENGTH_NORMAL[self.rank]

    def is_trump(self, trump_suit: Suit) -> bool:
        """Checks whether the card is a trump card.

        Args:
            trump_suit: The current trump suit.

        Returns:
            True if the card's suit matches the trump suit, False otherwise.
        """
        return self.suit == trump_suit

    def __repr__(self):
        return f"{self.rank.value}{self.suit.value}"

    def __eq__(self, other):
        return self.suit == other.suit and self.rank == other.rank
