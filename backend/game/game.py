"""Belote game orchestration.

Manages a full game consisting of multiple turns. A game ends when one
team reaches 501 points or more.
"""

from .player import Player, BotPlayer, HumanPlayer
import random
from .turn import Turn
from .deck import Deck


class Game:
    """Orchestrates a full Belote game across multiple turns.

    Assigns player indices, tracks team scores, and rotates the starting
    player after each turn. Teams are (South=0, North=2) vs (West=1, East=3).

    Attributes:
        players: Dictionary mapping player indices (0 to 3) to Player objects.
        team_ns_points: Accumulated points for the North-South team (players 0 and 2).
        team_ew_points: Accumulated points for the East-West team (players 1 and 3).
        starting_player_index: Index of the player who starts the current turn.
    """

    def __init__(self, players_list: list[Player]):
        """Initializes a Game and assigns indices to all players.

        Players are assigned indices 0 to 3 in the order they are provided.
        Teams are fixed: players 0 and 2 form one team, players 1 and 3 the other.

        Args:
            players_list: List of 4 Player objects to participate in the game.
        """
        for i, player in enumerate(players_list):
            player.set_player_index(i)
        self._players = {player.index: player for player in players_list}
        self._team_ns_points = 0
        self._team_ew_points = 0
        self._starting_player_index = random.choice([0, 1, 2, 3])
        self._game_over = False

    def start_game(self):
        """Starts the game by initializing the first turn.

        Creates a new Turn, deals cards, and runs the bidding phase up to
        the first human player or until a bot takes the contract.
        """
        self._new_turn()

    def _new_turn(self) -> dict:
        """Creates a new Turn and opens the bidding phase.

        Rotates the starting player, creates a fresh Turn with a new Deck,
        deals cards, and calls _open_bidding_phase() to make bots bid
        automatically until the human's turn or a bot takes the contract.
        """
        self._starting_player_index = (self._starting_player_index + 1) % 4
        self._turn = Turn(self._players, self._starting_player_index, Deck())
        self._turn.deal_before_bid()
        self._open_bidding_phase()
    
    def _open_bidding_phase(self):
        """Runs the bidding phase up to the first human decision point.

        Makes all bots bid until a human player is reached or bidding ends.
        If a bot takes the contract, resolves the bid immediately and makes
        bots play until the human's turn. If no one bids, the turn is aborted
        and a new one starts automatically via _new_turn().
        """
        self._make_bots_bid_until_human()
        #loop stops if a bot took or if the next player is human

        if self._turn.is_bidding_over():
            self._turn.resolve_second_round_bid()
            self._make_bots_play_until_human()

    def _make_bots_bid_until_human(self):
        """Makes all consecutive bot players bid until a human player is reached.

        Iterates through the bidding order, calling decide_bid() on each bot
        and submitting the result to the turn. Stops when a HumanPlayer is
        next to bid or when bidding ends (someone took or all passed).
        """
        if not self._turn.is_bidding_over():
            current_player = self._players[self._turn.current_player]
            while not isinstance(current_player, HumanPlayer):
                self._turn.bid_one_player(
                    current_player.index,
                    *current_player.decide_bid(self._turn.trump_card, self._turn.bidding_round)
                    )
                if self._turn.is_bidding_over():
                    break
                current_player = self._players[self._turn.current_player]

    def play_bid(self, takes: bool, suit=None):
        """Submits the human player's bid decision.

        Validates that bidding is still in progress, submits the human's
        decision, then makes remaining bots bid. If bidding ends, resolves
        the second round bid. If the turn is aborted, starts a new turn.
        Otherwise, makes bots play until the human's turn.

        Args:
            takes: True if the human accepts the contract, False to pass.
            suit: The chosen trump suit (required in round 2 when taking).

        Raises:
            ValueError: If the bidding phase is already over.
        """
        if self._turn.is_bidding_over():
            raise ValueError("Bidding phase is already over")
        else:
            current_player = self._players[self._turn.current_player]
            self._turn.bid_one_player(current_player.index, takes, suit=suit)
        self._make_bots_bid_until_human()

        if self._turn.is_bidding_over():
            self._turn.resolve_second_round_bid()
            if self._turn.turn_aborted:
                self._new_turn()
            else:
                self._make_bots_play_until_human()

    def play_card(self, card):
        """Submits the human player's card choice and advances the game state.

        Plays the human's card, then makes all subsequent bot players play
        automatically until the next human turn or the turn ends. If the
        turn ends, advances to the next turn.

        Args:
            card: The Card object the human player chooses to play.

        Raises:
            ValueError: If the card is not legally playable.
        """
        current_player = self._players[self._turn.current_player]
        self._turn.play_one_card(current_player.index, card)
        self._make_bots_play_until_human()
        if self._turn.is_turn_over():
            self._advance_next_turn()
    
    def _make_bots_play_until_human(self):
        """Makes all consecutive bot players play until a human player is reached.

        Iterates through the play order, calling play() on each bot and
        submitting the result to the turn. Stops when a HumanPlayer is
        next to play or when the turn ends.
        """
        if not self._turn.is_turn_over():
            current_player = self._players[self._turn.current_player]
            while not isinstance(current_player, HumanPlayer):
                self._play_bots(current_player)
                if self._turn.is_turn_over():
                    break
                current_player = self._players[self._turn.current_player]
        
    def _play_bots(self, player: Player):
        """Makes a single bot player choose and play a card.

        Takes a snapshot of the current cards played to avoid issues with
        list mutation, then calls play() on the bot and submits the result
        to the turn.

        Args:
            player: The bot Player instance whose turn it is to play.
        """
        cards_snapshot = list(self._turn.cards_played)
        card = player.play(
            self._turn.leading_player,
            self._turn.trump_suit,
            cards_snapshot
        )
        return self._turn.play_one_card(player.index, card)
    
    def _advance_next_turn(self):
        """Finalizes the current turn and starts a new one if the game continues.

        Retrieves final points from the turn, adds them to team totals,
        and either marks the game as over (resetting player indices) or
        starts a new turn.
        """
        turn_points = self._turn.get_points()
        self._add_point_one_turn(turn_points)
        if self.is_game_over():
            self._game_over = True
            self.reset_player_index()
        else:
            self._new_turn()

    def _add_point_one_turn(self, dict_points: dict):
        """Adds points from a completed turn to the team totals.

        Args:
            dict_points: Dictionary mapping player indices to their points for the turn.
        """
        self._team_ns_points += dict_points[0] + dict_points[2]
        self._team_ew_points += dict_points[1] + dict_points[3]

    def is_game_over(self):
        """Checks whether either team has reached or exceeded 501 points.

        Returns:
            True if the game is over, False otherwise.
        """
        return self._team_ew_points > 500 or self._team_ns_points > 500
    
    def get_player_hand(self, player_index: int):
        """Returns the current hand of the player at the given index.

        Args:
            player_index: The index of the player whose hand to retrieve.

        Returns:
            A list of Card objects representing the player's current hand.
        """
        player = self._players[player_index]
        return player.hand

    def get_status(self):
        """Returns a snapshot of the current game state for the communication layer.

        Includes game-level information (scores, game over flag) and
        turn-level information (current player, cards played, trump suit, etc.).

        Returns:
            A dictionary with the following keys:
                game_over: True if the game has ended.
                team_ns_points: Accumulated points for the NS team.
                team_ew_points: Accumulated points for the EW team.
                cards_played: Cards played in the current trick.
                cards_played_last_trick: Cards played in the previous trick.
                current_player: Index of the player whose turn it is.
                starting_player: Index of the player who leads the current trick.
                card_shown: The face-up card that proposed the trump suit.
                trump_suit: The current trump suit.
                taker: Index of the player who took the contract, or None.
                bid_round: The current bidding round (1 or 2).
        """
        return {
            'game_over': self._game_over,
            'team_ns_points': self._team_ns_points,
            'team_ew_points': self._team_ew_points,
            'cards_played': self._turn.cards_played,
            'cards_played_last_trick': self._turn.cards_played_last_trick,
            'current_player': self._turn.current_player,
            'starting_player': self._turn.starting_player_index,
            'card_shown': self._turn.trump_card,
            'trump_suit': self._turn.trump_suit,
            'taker': self._turn.taker,
            'bid_round': self._turn.bidding_round
        }
    
    def get_human_player_index(self) -> int:
        """Returns the index of the first human player in the game.

        Returns:
            The integer index of the HumanPlayer, or None if no human player exists.
        """
        return next(
            (i for i in self._players if isinstance(self._players[i], HumanPlayer)),
            None
        )
    
    def reset_player_index(self):
        """Resets all player indices to None at the end of the game.

        Allows Player objects to be reused in a new game without stale state.
        """
        for player in self._players.values():
            player.set_player_index(None)
