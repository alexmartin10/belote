"""Belote turn logic.

A turn (manche) consists of one bidding phase followed by 8 tricks.
Turn orchestrates Bid, Trick, and Player without knowing anything
about the communication layer above it.

Glossary:
    trick: A single trick (pli in French).
    turn: A full round of 8 tricks (manche in French).
"""

from .deck import Deck
from .player import Player
from .trick import Trick
from .bid import Bid
from .card import Card, Rank, Suit


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

    def __init__(self, players: dict[int, Player], starting_player_index: int, deck: Deck):
        """Initializes a Turn.

        Args:
            players: Dictionary mapping player indices to Player objects.
            starting_player_index: Index of the player who starts the turn.
            deck: A fresh Deck instance for this turn.
        """
        self._players = players
        self.starting_player_index = starting_player_index
        self._deck = deck
        self._order = [(starting_player_index + k) % 4 for k in range(4)]
        self._points = {0: 0, 1: 0, 2: 0, 3: 0}
        self._tricks_played = 0
        self._trick = None
        self._turn_aborted = None
        self._turn_finished = None
        self._player_has_belote_rebelote = None
        self._cards_played_last_trick = None

    def deal_before_bid(self):
        """Deals cards and runs the bidding phase.

        Deals 5 cards to each player, reveals the trump card, then runs
        the bidding phase. If a player takes the contract, completes the
        deal to 8 cards per player. If no one bids, marks the turn as aborted.
        """
        hands_before_bid = self._deck.deal_before_bid()
        self.trump_card = self._deck.trump_card()
        self._bid = Bid(self._order, self.trump_card)

        for index, hand in zip(self._order, hands_before_bid):
            self._players[index].make_hand(hand)
        
        self._sort_players_hand(self.trump_suit)

    def resolve_second_round_bid(self):
        if self._bid.current_bidder is None:
            self._turn_aborted = True
        else:
            hands = [self._players[i].hand for i in range(4)]
            self._deck.deal_after_bid(self.taker, hands)
            self._sort_players_hand(self.trump_suit)
            self._look_for_belote_rebelote()
            self._trick = Trick(self._players, self.starting_player_index, self.trump_suit)

    def _sort_players_hand(self, trump_suit):
        for player in self._players.values():
            player.sort_hand(trump_suit)
    
    def bid_one_player(self, player_index, takes, suit=None):
        self._bid.receive_bid(player_index, takes, suit=suit)
    
    def play_one_card(self, player_index, card):
        self._trick.receive_card(player_index, card)

        if self._trick.is_trick_over():
            self._advance_next_trick()

    def _advance_next_trick(self):
        self._tricks_played += 1
        self._points[self.leading_player] += self._trick.points
        self.starting_player_index = self.leading_player

        if self._tricks_played == 8:
            self._points[self.leading_player] += 10
            self._turn_finished = True
        
        else:
            self._cards_played_last_trick = {
                index: card for index, card in zip(self._order, self.cards_played)
            }
            self._order = [(self.starting_player_index + k) % 4 for k in range(4)]
            self._trick = Trick(self._players, self.starting_player_index, self.trump_suit)

    def _look_for_belote_rebelote(self):
        for player in self._players.values():
            trump_queen = Card(Rank.QUEEN, self.trump_suit)
            trump_king = Card(Rank.KING, self.trump_suit)
            if trump_queen in player.hand and trump_king in player.hand:
                self._player_has_belote_rebelote = player.index
                break

    def _check_contract(self) -> bool:
        """Checks whether the contracting team fulfilled their contract.

        The contracting team must score more than 81 points to succeed.

        Returns:
            True if the contract is fulfilled, False otherwise.
        """
        points_team_taking_contract = (
            self._points[self.taker] + self._points[(self.taker + 2) % 4]
        )
        return points_team_taking_contract > 81
    
    def _check_zero_points(self):
        """
        Returns the index of a team member from the team that
        scored 0 points. If both teams have scored points, return None.
        """
        points_team_taking_contract = (
            self._points[self.taker] + self._points[(self.taker + 2) % 4]
        )
        if points_team_taking_contract == 0:
            return self.taker
        elif points_team_taking_contract == 162:
            return (self.taker + 1) % 4
        
        return None

    def get_points(self):
        """Applies contract failure penalty if the contracting team lost.

        If the contract is fulfilled, points are left unchanged and computed
        at the Game layer. If not, the opposing team scores 162 and the
        contracting team scores 0.
        """
        team_member_with_no_points = self._check_zero_points()
        if team_member_with_no_points is not None:
            self._points = {
                team_member_with_no_points: 0,
                (team_member_with_no_points + 1) % 4: 252,
                (team_member_with_no_points + 2) % 4: 0,
                (team_member_with_no_points + 3) % 4: 0
            }

        elif not self._check_contract():
            self._points = {
                self._bid.taker: 0,
                (self._bid.taker + 1) % 4: 162,
                (self._bid.taker + 2) % 4: 0,
                (self._bid.taker + 3) % 4: 0
            }

        if self._player_has_belote_rebelote is not None:
            self._points[self._player_has_belote_rebelote] += 20

        return self._points
    
    def points(self, points):
        self._points = points
    
    @property
    def current_player(self):
        if self._trick is None:
            return self._bid.current_bidder
        else:
            return self._trick.current_player
    
    @property
    def leading_player(self):
        if self._trick is None:
            return None
        else:
            return self._trick.leading_player
    
    @property
    def cards_played(self):
        if self._trick is None:
            return []
        else:
            return self._trick.cards_played
    
    @property
    def cards_played_last_trick(self):
        if self._cards_played_last_trick is None:
            return {}
        else:
            return self._cards_played_last_trick
    
    @property
    def bidding_round(self):
        return self._bid.round
    
    @property
    def taker(self):
        return self._bid.taker
    
    @property
    def trump_suit(self):
        return self._bid.trump_suit
    
    @property
    def turn_aborted(self):
        return self._turn_aborted
    
    def is_turn_over(self) -> bool:
        """Checks whether the turn has ended (either finished or aborted).

        Returns:
            True if the turn is over, False otherwise.
        """
        return bool(self._turn_aborted or self._turn_finished)
    
    def is_bidding_over(self):
        return self._bid.is_bidding_over()
    