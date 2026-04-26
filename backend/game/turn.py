"""Belote turn logic.

A turn (manche) consists of one bidding phase followed by 8 tricks.
Turn orchestrates Bid, tTrick, and Player without knowing anything
about the communication layer above it.

Glossary:
    trick: A single trick (pli in French).
    turn: A full round of 8 tricks (manche in French).
"""

from .deck import Deck
from .player import BotPlayer
from .trick import Trick
from .bid import Bid


class Turn:
    """Orchestrates a full Belote round (bidding + 8 tricks).

    Acts as the top-level coordinator of the game engine for a single round.
    Delegates bidding to Bid and trick logic to Trick. Does not block on user
    input; all decisions are produced by Player subclasses and passed in.

    Attributes:
        players: Dictionary mapping player indices to Player objects.
        starting_player_index: Index of the player who leads the first trick.
        deck: The Deck instance used for this turn.
        order: Ordered list of player indices starting from starting_player_index.
        points: Dictionary mapping player indices to their accumulated points.
        turn_aborted: True if no player took the contract; None otherwise.
        turn_finished: True after all 8 tricks have been played; None otherwise.
        bid: The Bid instance managing the bidding phase.
        trump_card: The face-up card that proposed the trump suit.
    """

    def __init__(self, players: dict[int, BotPlayer], starting_player_index: int, deck: Deck):
        """Initializes a Turn.

        Args:
            players: Dictionary mapping player indices to Player objects.
            starting_player_index: Index of the player who starts the turn.
            deck: A fresh Deck instance for this turn.
        """
        self.players = players
        self.starting_player_index = starting_player_index
        self.deck = deck
        self.order = [(starting_player_index + k) % 4 for k in range(4)]
        self.points = {0: 0, 1: 0, 2: 0, 3: 0}
        self.tricks_played = 0
        self.turn_aborted = None
        self.turn_finished = None

    def deal(self):
        """Deals cards and runs the bidding phase.

        Deals 5 cards to each player, reveals the trump card, then runs
        the bidding phase. If a player takes the contract, completes the
        deal to 8 cards per player. If no one bids, marks the turn as aborted.
        """
        hands_before_bid = self.deck.deal_before_bid()
        self.trump_card = self.deck.trump_card()
        self.bid = Bid(self.order, self.trump_card)

        for index, hand in zip(self.order, hands_before_bid):
            self.players[index].make_hand(hand)

        while not self.bid.is_bidding_over():
            current_player = self.players[self.bid.current_bidder]
            self.bid.receive_bid(
                current_player.index,
                current_player.decide_bid(self.bid.trump_card),
                suit=None
            )

        if self.bid.current_bidder is None:
            self.turn_aborted = True
        else:
            hands = [self.players[i].hand for i in range(4)]
            self.deck.deal_after_bid(self.bid.taker, hands)
            self.trick = Trick(self.players, self.starting_player_index, self.bid.trump_suit)

    def new_turn(self):
        """Placeholder for starting a new turn.

        Responsibility of the Game layer. Raises NotImplementedError
        if called directly on Turn.

        Raises:
            NotImplementedError: Always.
        """
        raise NotImplementedError
    
    def play_one_card(self, player_index, card):
        self.trick.receive_card(player_index, card)

        if self.trick.is_trick_over():
            self._advance_next_trick()

    def _advance_next_trick(self):
        self.tricks_played += 1
        self.points[self.trick.leading_player] += self.trick.points
        self.starting_player_index = self.trick.leading_player

        if self.tricks_played == 8:
            self.points[self.trick.leading_player] += 10
            self.turn_finished = True
        
        else:
            self.trick = Trick(self.players, self.starting_player_index, self.trump_card.suit)

    def _check_contract(self) -> bool:
        """Checks whether the contracting team fulfilled their contract.

        The contracting team must score more than 81 points to succeed.

        Returns:
            True if the contract is fulfilled, False otherwise.
        """
        points_team_taking_contract = (
            self.points[self.bid.taker] + self.points[(self.bid.taker + 2) % 4]
        )
        return points_team_taking_contract > 81

    def _get_points(self):
        """Applies contract failure penalty if the contracting team lost.

        If the contract is fulfilled, points are left unchanged and computed
        at the Game layer. If not, the opposing team scores 162 and the
        contracting team scores 0.
        """
        if not self._check_contract():
            self.points = {
                self.bid.taker: 0,
                (self.bid.taker + 1) % 4: 162,
                (self.bid.taker + 2) % 4: 0,
                (self.bid.taker + 3) % 4: 0
            }

    def get_status(self) -> dict:
        """Returns the current turn status for the communication layer.

        Returns:
            A dictionary with the following key:
                points: Dictionary mapping player indices to their points.
        """
        return {
            'points': self.points,
            'current_player': self.trick.current_player,
            'leading_player': self.trick.leading_player,
            'trump_suit': self.trump_card.suit,
            'cards_played': self.trick.cards_played
        }

    def is_turn_over(self) -> bool:
        """Checks whether the turn has ended (either finished or aborted).

        Returns:
            True if the turn is over, False otherwise.
        """
        return bool(self.turn_aborted or self.turn_finished)

    def main(self) -> dict:
        """Runs a complete turn: deals, bids, plays, and scores.

        Returns:
            A dictionary mapping player indices to their final point totals.
            Returns all zeros if the turn was aborted (no taker).
        """
        self.deal()
        if not self.turn_aborted:
            self.play_tricks()
            self._get_points()
        return self.points
