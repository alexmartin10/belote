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
        self.players = {player.index: player for player in players_list}
        self.team_ns_points = 0
        self.team_ew_points = 0
        self.starting_player_index = random.choice([0, 1, 2, 3])
        self.game_over = False

    def start_game(self):
        self._new_turn()

    def add_point_one_turn(self, dict_points: dict):
        """Adds points from a completed turn to the team totals.

        Args:
            dict_points: Dictionary mapping player indices to their points for the turn.
        """
        self.team_ns_points += dict_points[0] + dict_points[2]
        self.team_ew_points += dict_points[1] + dict_points[3]

    def _new_turn(self) -> dict:
        """Creates and runs a new Turn, returning the resulting points.

        Returns:
            A dictionary mapping player indices to their points for this turn.
        """
        self.turn = Turn(self.players, self.starting_player_index, Deck())
        self.turn.deal_before_bid()

    def play_bid(self, takes):
        if not self.turn.bid.is_bidding_over():
            current_player = self.players[self.turn.get_current_player()]
            while not isinstance(current_player, HumanPlayer):
                self.turn.bid_one_player(
                    current_player.index,
                    current_player.decide_bid(self.turn.bid.trump_card)
                    )
                if self.turn.bid.is_bidding_over():
                    break
                current_player = self.players[self.turn.get_current_player()]

            self.turn.bid_one_player(current_player.index, takes)

            if not self.turn.bid.is_bidding_over():
                current_player = self.players[self.turn.get_current_player()]

            while not isinstance(current_player, HumanPlayer):
                self.turn.bid_one_player(
                    current_player.index,
                    current_player.decide_bid(self.turn.bid.trump_card)
                    )
                if self.turn.bid.is_bidding_over():
                    break
                current_player = self.players[self.turn.get_current_player()]

            if self.turn.bid.is_bidding_over():
                self.turn.resolve_second_round_bid()
                if self.turn.turn_aborted == True:
                    self._new_turn()

    def play_card(self, card):
        while self.turn.turn_aborted:
            self._new_turn()
        if not self.turn.is_turn_over():
            turn_status = self.turn.get_status()
            current_player = self.players[turn_status['current_player']]
            while not isinstance(current_player, HumanPlayer):
                self._play_bots(current_player, turn_status)
                if self.turn.is_turn_over():
                    break
                turn_status = self.turn.get_status()
                current_player = self.players[turn_status['current_player']]

            self.turn.play_one_card(current_player.index, card)
            if not self.turn.is_turn_over():
                turn_status = self.turn.get_status()
                current_player = self.players[turn_status['current_player']]

            while not (isinstance(current_player, HumanPlayer) or self.turn.is_turn_over()):
                self._play_bots(current_player, turn_status)
                if self.turn.is_turn_over():
                    break
                turn_status = self.turn.get_status()
                current_player = self.players[turn_status['current_player']]
            if self.turn.is_turn_over():
                self._advance_next_turn()
        
    def _play_bots(self, player: Player, status):
        return self.turn.play_one_card(
                player.index,
                card=player.play(
                    status['leading_player'],
                    status['trump_suit'],
                    status['cards_played']
                )
            )
    
    def _advance_next_turn(self):
        turn_points = self.turn.get_status()['points']
        self.add_point_one_turn(turn_points)
        if self.is_game_over():
            self.game_over = True
            self.reset_player_index()
        else:
            self.starting_player_index = (self.starting_player_index + 1) % 4
            self._new_turn()

    def is_game_over(self):
        return self.team_ew_points > 500 or self.team_ns_points > 500
    
    def get_player_hand(self, player: Player):
        return player.hand

    def get_status(self):
        turn_status = self.turn.get_status()
        return {
            'game_over': self.game_over,
            'team_ns_points': self.team_ns_points,
            'team_ew_points': self.team_ew_points,
            'cards_played': turn_status['cards_played'],
            'current_player': turn_status['current_player'],
            'starting_player': turn_status['starting_player'],
            'card_shown': turn_status['card_shown'],
            'trump_suit': turn_status['trump_suit'],
            'taker': self.turn.bid.taker
        }
    
    def reset_player_index(self):
        """Resets all player indices to None at the end of the game.

        Allows Player objects to be reused in a new game without stale state.
        """
        for player in self.players.values():
            player.set_player_index(None)