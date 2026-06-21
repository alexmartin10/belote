"""Belote deck model.

Handles the construction and dealing of the 32-card Belote deck.
"""

from .card import Card, Suit, Rank
import random


class Deck:
    """A 32-card Belote deck.

    Handles shuffling and dealing cards before and after the bidding phase.

    Attributes:
        num_players: Number of players in the game (always 4).
        cards: The ordered list of all 32 cards in the deck.
        next_card_index: Index of the next card to be dealt.
    """
    NUM_PLAYERS = 4

    def __init__(self):
        """Initializes a full 32-card deck and builds it."""
        self._build()
        self._next_card_index = None

    def _build(self):
        """Builds the full deck of 32 cards (7 through Ace, all 4 suits)."""
        self._cards = [
            Card(rank, suit)
            for rank in Rank
            for suit in Suit
        ]

    def _shuffle(self):
        """Shuffles the deck in place."""
        random.shuffle(self._cards)

    def deal_before_bid(self) -> list[list[Card]]:
        """Shuffles the deck and deals 5 cards to each player before bidding.

        Cards are dealt in two passes. The pass sizes are randomly chosen
        between [2, 3] and [3, 2], matching real Belote conventions.
        Player order is not handled here; hands are assigned to players
        by the caller.

        Returns:
            A list of 4 hands, each containing 5 Card objects.
        """
        hands = [[] for _ in range(self.NUM_PLAYERS)]
        self._shuffle()
        batch = random.choice([[2, 3], [3, 2]])
        self._next_card_index = 0

        for n in batch:
            for i in range(self.NUM_PLAYERS):
                for _ in range(n):
                    hands[i].append(self._cards[self._next_card_index])
                    self._next_card_index += 1

        return hands

    def trump_card(self) -> Card:
        """Returns the face-up card used to propose the trump suit.

        Must be called after deal_before_bid(). Does not advance
        next_card_index — the card is only consumed after a player bids.

        Returns:
            The card at the current next_card_index.
        """
        if self._next_card_index is None:
            raise IndexError("Must call deal_before_bid before seeing trump card.")
        return self._cards[self._next_card_index]

    def deal_after_bid(self, taker_index: int, hands: list[list]) -> None:
        """Complete the deal after a player has accepted the contract.

        The taker receives the face-up trump card plus 2 additional cards
        (8 total). All other players receive 3 additional cards (8 total).
        The provided hands are modified in place.

        Args:
            taker_index: The index of the player who accepted the contract.
            hands: The list of current hands to complete in place.

        Raises:
            IndexError: If called before ``deal_before_bid``.
        """
        if self._next_card_index is None:
            raise IndexError("Must call deal_before_bid before dealing others cards.")
        
        hands[taker_index].append(self._cards[self._next_card_index])
        self._next_card_index += 1
        n_cards_to_distribute = 3

        for i in range(self.NUM_PLAYERS):
            if i == taker_index:
                for _ in range(n_cards_to_distribute - 1):
                    hands[i].append(self._cards[self._next_card_index])
                    self._next_card_index += 1
            else:
                for _ in range(n_cards_to_distribute):
                    hands[i].append(self._cards[self._next_card_index])
                    self._next_card_index += 1
