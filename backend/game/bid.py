"""Belote bidding phase.

Manages the two-round bidding phase during which players decide
whether to take the contract and which suit will be trump.
"""

from .card import Card, Suit

ALL_SUITS = [suit for suit in Suit]


class Bid:
    """Handles the bidding phase of a Belote turn.

    The bidding phase consists of up to two rounds. In the first round,
    players may accept the proposed trump suit. In the second round, they
    may name any other suit as trump. If no player bids in either round,
    the turn is aborted.

    A single bid_index running from 0 to 7 tracks progress across both
    rounds, avoiding explicit round-switching logic.

    Attributes:
        order: Ordered list of player indices for this turn.
        trump_card: The face-up card that proposes the initial trump suit.
        trump_suit: The current trump suit (may change in round 2).
        taker: Index of the player who accepted the contract, or None.
        current_bidder: Index of the player whose turn it is to bid.
        bid_index: Current position in the bidding sequence (0 to 7).
        round: Current bidding round (1 or 2).
        possible_suits: Available suits in round 2 (excludes the initial trump suit).
    """

    def __init__(self, order: list[int], trump_card: Card):
        """Initializes the bidding phase.

        Args:
            order: Ordered list of player indices for this turn.
            trump_card: The face-up card proposing the initial trump suit.
        """
        self.order = order
        self.trump_card = trump_card
        self.trump_suit = trump_card.suit
        self.taker = None
        self.current_bidder = self.order[0]
        self.bid_index = 0
        self.round = 1

    def _advance_next_bidder(self):
        """Advances the bidding to the next player.

        Handles the transition from round 1 to round 2 when all four players
        have passed. Sets current_bidder to None if all 8 bids are exhausted.
        """
        self.bid_index += 1

        if self.bid_index < 4:
            self.current_bidder = self.order[self.bid_index]
        elif self.bid_index == 4:
            self.round = 2
            self.possible_suits = [s for s in ALL_SUITS if s != self.trump_card.suit]
            self.current_bidder = self.order[self.bid_index % 4]
        elif self.bid_index < 8:
            self.current_bidder = self.order[self.bid_index % 4]
        else:
            self.current_bidder = None

    def receive_bid(self, player_index: int, takes: bool, suit: Suit = None) -> dict:
        """Processes a bid from a player.

        If the player takes, the contract is assigned to them. In round 2,
        the player must also specify a valid trump suit. If the player passes,
        the bidding advances to the next player.

        Args:
            player_index: Index of the player submitting the bid.
            takes: True if the player accepts the contract, False to pass.
            suit: The chosen trump suit (required in round 2 when taking).

        Returns:
            The current bidding state as a dictionary.

        Raises:
            ValueError: If it is not the player's turn to bid.
            ValueError: If the player tries to name the already-proposed suit in round 2.
        """
        if player_index != self.current_bidder:
            raise ValueError("Not this player turn")

        if takes:
            if self.round == 2:
                if suit not in self.possible_suits:
                    raise ValueError("Trump suit must be different than the one showed")
                self.trump_suit = suit
            self.taker = player_index
        else:
            self._advance_next_bidder()

        return self.get_state()

    def is_bidding_over(self) -> bool:
        """Checks whether the bidding phase has ended.

        Bidding ends when a player takes the contract or when all players
        have passed in both rounds.

        Returns:
            True if bidding is over, False otherwise.
        """
        return self.taker is not None or self.current_bidder is None

    def get_state(self) -> dict:
        """Returns the current bidding state for the communication layer.

        Returns:
            A dictionary with the following keys:
                phase: Always 'bidding'.
                round: Current round (1 or 2).
                current_bidder: Index of the player whose turn it is, or None.
                trump_suit: The current trump suit.
                taker: Index of the player who took the contract, or None.
        """
        return {
            'phase': 'bidding',
            'round': self.round,
            'current_bidder': self.current_bidder,
            'trump_suit': self.trump_suit,
            'taker': self.taker,
        }
