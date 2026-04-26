"""Belote trick logic.

Manages a single trick: card validation, trick winner determination,
and point counting.
"""

from .card import Suit
from .player import Player

import numpy as np


class Trick:
    """Manages a single trick in a Belote turn.

    Validates each card played, tracks the current leader, and computes
    the trick's point value once all four players have played.

    Attributes:
        current_player: Index of the player whose turn it is, or None when the trick is over.
        starting_player: Index of the player who leads the trick.
        trump_suit: The current trump suit.
        cards_played: Ordered list of cards played in this trick.
        players: Dictionary mapping player indices to Player objects.
        leading_player: Index of the player currently winning the trick.
        points: Total point value of the trick, set when the trick ends.
    """

    def __init__(self, players: dict[int, Player], starting_player_index: int, trump_suit: Suit):
        """Initializes a Trick.

        Args:
            players: Dictionary mapping player indices to Player objects.
            starting_player_index: Index of the player who leads this trick.
            trump_suit: The current trump suit.
        """
        self.current_player = starting_player_index
        self.starting_player = starting_player_index
        self.trump_suit = trump_suit
        self.cards_played = []
        self.players = players
        self.leading_player = starting_player_index
        self.points = None

    def receive_card(self, player_index: int, card) -> dict:
        """Processes a card played by a player.

        Validates that it is the player's turn and that the card is legally
        playable. If valid, adds the card to the trick, removes it from the
        player's hand, and advances to the next player.

        Args:
            player_index: Index of the player playing the card.
            card: The Card object being played.

        Returns:
            The current trick state as a dictionary.

        Raises:
            ValueError: If it is not the player's turn.
            ValueError: If the card is not in the player's list of playable cards.
        """
        if player_index != self.current_player:
            raise ValueError("Not this player's turn")

        player = self.players[player_index]
        if card not in player.playable_cards(self.cards_played, self.trump_suit):
            raise ValueError(
                f"Can't play this card: player {player_index} played {card}, "
                f"but playable cards were {player.playable_cards(self.cards_played, self.trump_suit)}"
            )

        self.cards_played.append(card)
        player.remove_card_played(card)
        self._advance_next_player()

        return self.get_state()

    def _advance_next_player(self):
        """Advances the trick to the next player.

        Wraps around using modulo 4. When the trick returns to the starting
        player, the trick is marked as over and points are counted.
        """
        self.current_player = (self.current_player + 1) % 4
        self._get_leader()

        if self.current_player == self.starting_player:
            self.current_player = None
            self._count_points()

    def is_trick_over(self) -> bool:
        """Checks whether all four players have played.

        Returns:
            True if the trick is over, False otherwise.
        """
        return self.current_player is None

    def get_state(self) -> dict:
        """Returns the current trick state for the communication layer.

        Returns:
            A dictionary with the following keys:
                current_player: Index of the next player to play, or None.
                cards_played: Ordered list of cards played so far.
                leading_player: Index of the player currently winning the trick.
                points: Total point value of the trick, or None if not yet complete.
        """
        return {
            'current_player': self.current_player,
            'cards_played': self.cards_played,
            'leading_player': self.leading_player,
            'points': self.points
        }

    def _get_leader(self):
        """Updates the leading player based on the cards played so far.

        The leader is determined by comparing card strengths. Trump cards
        always outrank non-trump cards due to the +100 strength bonus.
        """
        strengths = [card.strength(self.trump_suit) for card in self.cards_played]
        arg = int(np.argmax(strengths))
        self.leading_player = (self.starting_player + arg) % 4

    def _count_points(self):
        """Sums the point values of all cards played in the trick.

        Called automatically when the trick ends. Result is stored in self.points.
        """
        self.points = sum(card.points(self.trump_suit) for card in self.cards_played)
