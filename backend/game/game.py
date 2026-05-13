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
        self._new_turn()

    def _new_turn(self) -> dict:
        """Creates and runs a new Turn, returning the resulting points.

        Returns:
            A dictionary mapping player indices to their points for this turn.
        """
        self._starting_player_index = (self._starting_player_index + 1) % 4
        self._turn = Turn(self._players, self._starting_player_index, Deck())
        self._turn.deal_before_bid()
        self._open_bidding_phase()
    
    def _open_bidding_phase(self):
        self._make_bots_bid_until_human()
        #loop stops if a bot took or if the next player is human

        if self._turn.is_bidding_over():
            self._turn.resolve_second_round_bid()
            self._make_bots_play_until_human()

    def _make_bots_bid_until_human(self):
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
        current_player = self._players[self._turn.current_player]
        self._turn.play_one_card(current_player.index, card)
        self._make_bots_play_until_human()
        if self._turn.is_turn_over():
            self._advance_next_turn()
    
    def _make_bots_play_until_human(self):
        if not self._turn.is_turn_over():
            current_player = self._players[self._turn.current_player]
            while not isinstance(current_player, HumanPlayer):
                self._play_bots(current_player)
                if self._turn.is_turn_over():
                    break
                current_player = self._players[self._turn.current_player]
        
    def _play_bots(self, player: Player):
        cards_snapshot = list(self._turn.cards_played)
        card = player.play(
            self._turn.leading_player,
            self._turn.trump_suit,
            cards_snapshot
        )
        return self._turn.play_one_card(player.index, card)
    
    def _advance_next_turn(self):
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
        return self._team_ew_points > 500 or self._team_ns_points > 500
    
    def get_player_hand(self, player_index: int):
        player = self._players[player_index]
        return player.hand

    def get_status(self):
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