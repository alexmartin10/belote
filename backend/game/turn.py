"""Belote turn logic.

A turn (manche) consists of one bidding phase followed by 8 tricks.
Turn orchestrates Bid, Trick, and Player without knowing anything
about the communication layer above it.

Glossary:
    trick: A single trick (pli in French).
    turn: A full round of 8 tricks (manche in French).
"""

from .deck import Deck
from .player import Player, BotPlayer
from .trick import Trick
from .bid import Bid
from .card import Card, Rank, Suit
from functools import reduce

class Turn:
    """Orchestrates a full Belote round (bidding + 8 tricks).

    Acts as the top-level coordinator of the game engine for a single round.
    Delegates bidding to Bid and trick logic to Trick. Does not block on user
    input; all decisions are produced by Player subclasses and passed in.

    Attributes:
        starting_player_index: Index of the player who leads the current trick.
        trump_card: The face-up card that proposed the trump suit.
        current_player: Index of the player whose turn it is (property).
        leading_player: Index of the player currently winning the trick (property).
        cards_played: Cards played so far in the current trick (property).
        cards_played_last_trick: Mapping of player index to card for the last trick (property).
        trump_suit: The current trump suit (property).
        taker: Index of the player who took the contract, or None (property).
        bidding_round: The current bidding round, 1 or 2 (property).
        turn_aborted: True if no player took the contract, None otherwise (property).
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
        """Deals 5 cards to each player and initializes the bidding phase.

        Shuffles the deck, deals cards in two passes, reveals the trump card,
        and creates a Bid instance. Hands are sorted by suit after dealing.
        Does not run the bidding itself — bidding is driven externally via
        bid_one_player().
        """
        hands_before_bid = self._deck.deal_before_bid()
        self.trump_card = self._deck.trump_card()
        self._bid = Bid(self._order, self.trump_card)

        for index, hand in zip(self._order, hands_before_bid):
            self._players[index].make_hand(hand)
        
        self._sort_players_hand(self.trump_suit)

    def resolve_second_round_bid(self):
        """Finalizes the turn after bidding is complete.

        If no player took the contract (current_bidder is None), marks the
        turn as aborted. Otherwise, completes the deal to 8 cards per player,
        sorts hands, checks for belote-rebelote, and creates the first Trick.
        """
        if self._bid.current_bidder is None:
            self._turn_aborted = True
        else:
            hands = [self._players[i].hand for i in range(4)]
            self._deck.deal_after_bid(self.taker, hands)
            self._sort_players_hand(self.trump_suit)
            self._look_for_belote_rebelote()
            self._trick = Trick(self._players, self.starting_player_index, self.trump_suit)

    def _sort_players_hand(self, trump_suit):
        """Sorts all players' hands by suit and strength.

        Trump suit is placed first, with cards sorted from strongest to weakest
        within each suit. Delegates to each Player's sort_hand() method.

        Args:
            trump_suit: The current trump suit to prioritize in the sort.
        """
        for player in self._players.values():
            player.sort_hand(trump_suit)
    
    def bid_one_player(self, player_index, takes, suit=None):
        """Submits a single bid decision to the bidding phase.

        Delegates to Bid.receive_bid(). Called once per player per bidding turn,
        whether the player is a bot or the decision comes from the API.

        Args:
            player_index: Index of the player submitting the bid.
            takes: True if the player accepts the contract, False to pass.
            suit: The chosen trump suit (required in round 2 when taking).

        Raises:
            ValueError: If it is not the player's turn to bid.
            ValueError: If an invalid suit is provided in round 2.
        """
        self._bid.receive_bid(player_index, takes, suit=suit)
    
    def play_one_card(self, player_index, card):
        """Submits a single card to the current trick.

        Delegates validation and state advancement to Trick.receive_card().
        If the trick ends after this card, advances to the next trick or
        marks the turn as finished.

        Args:
            player_index: Index of the player playing the card.
            card: The Card object being played.

        Raises:
            ValueError: If it is not the player's turn.
            ValueError: If the card is not legally playable.
        """
        self._trick.receive_card(player_index, card)

        if self._trick.is_trick_over():
            self._advance_next_trick()

    def _advance_next_trick(self):
        """Updates state after a trick ends and prepares the next one.

        Increments the trick counter, awards points to the trick winner,
        updates the starting player for the next trick. On the 8th trick,
        awards the 10 de der bonus and marks the turn as finished. Otherwise,
        saves the last trick's cards and creates a new Trick instance.
        """
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
            self.save_trick_for_bots()
            self._order = [(self.starting_player_index + k) % 4 for k in range(4)]
            self._trick = Trick(self._players, self.starting_player_index, self.trump_suit)
    
    def save_trick_for_bots(self):
        for player in self._players.values():
            if isinstance(player, BotPlayer):
                player.save_trick(list(self.cards_played_last_trick.values()))

    def _look_for_belote_rebelote(self):
        """Detects whether any player holds both the King and Queen of trump.

        If found, stores that player's index in _player_has_belote_rebelote
        so that 20 bonus points can be awarded when get_points() is called.
        Only the first matching player is recorded.
        """
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
        """Returns a team member index from the team that scored 0 points (capot).

        Checks whether the contracting team scored all 162 points (capot against
        the opposing team) or 0 points (capot against the contracting team).

        Returns:
            The index of a player from the team that scored 0 points, or None
            if both teams have scored points.
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
        """Computes and returns the final points for this turn.

        Applies scoring rules in order:
        - If a capot occurred, the winning team scores 252 and the other 0.
        - If the contract was not fulfilled, the opposing team scores 162 and
          the contracting team scores 0.
        - If belote-rebelote was detected, adds 20 bonus points to that player,
          regardless of contract outcome.

        Returns:
            A dictionary mapping player indices to their final point totals.
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
        """Sets the internal points dictionary directly.

        Used in tests to inject specific point distributions for scoring
        logic verification without playing a full turn.

        Args:
            points: A dictionary mapping player indices to point values.
        """
        self._points = points
    
    @property
    def current_player(self):
        """Returns the index of the player whose turn it is.

        During bidding, returns the current bidder. During trick play,
        returns the current trick player. Returns None when a phase is over.

        Returns:
            An integer player index, or None if the current phase is complete.
        """
        if self._trick is None:
            return self._bid.current_bidder
        else:
            return self._trick.current_player
    
    @property
    def leading_player(self):
        """Returns the index of the player currently winning the trick.

        Returns None during the bidding phase before any trick has started.

        Returns:
            An integer player index, or None if no trick is in progress.
        """
        if self._trick is None:
            return None
        else:
            return self._trick.leading_player
    
    @property
    def cards_played(self):
        """Returns the cards played so far in the current trick.

        Returns an empty list during the bidding phase before any trick has started.

        Returns:
            A list of Card objects played in the current trick.
        """
        if self._trick is None:
            return []
        else:
            return self._trick.cards_played
    
    @property
    def cards_played_last_trick(self):
        """Returns a mapping of player indices to the card each played in the last trick.

        Returns an empty dict if no trick has been completed yet.

        Returns:
            A dictionary mapping player index to Card for the previous trick,
            or an empty dict if this is the first trick.
        """
        if self._cards_played_last_trick is None:
            return {}
        else:
            return self._cards_played_last_trick
    
    @property
    def bidding_round(self):
        """Returns the current bidding round (1 or 2).

        Returns:
            An integer indicating the active bidding round.
        """
        return self._bid.round
    
    @property
    def taker(self):
        """Returns the index of the player who accepted the contract, or None.

        Returns:
            An integer player index if someone has taken, otherwise None.
        """
        return self._bid.taker
    
    @property
    def trump_suit(self):
        """Returns the current trump suit.

        In round 1 this is the suit of the face-up card. In round 2 it may
        have been changed by the player who took the contract.

        Returns:
            A Suit enum value representing the current trump suit.
        """
        return self._bid.trump_suit
    
    @property
    def turn_aborted(self):
        """Returns True if the turn was aborted because no player took the contract.

        Returns:
            True if aborted, None otherwise.
        """
        return self._turn_aborted
    
    def is_turn_over(self) -> bool:
        """Checks whether the turn has ended (either finished or aborted).

        Returns:
            True if the turn is over, False otherwise.
        """
        return bool(self._turn_aborted or self._turn_finished)
    
    def is_bidding_over(self):
        """Checks whether the bidding phase has ended.

        Delegates to Bid.is_bidding_over().

        Returns:
            True if bidding is over, False otherwise.
        """
        return self._bid.is_bidding_over()
