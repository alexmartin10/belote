"""Belote game orchestration.

Manages a full game consisting of multiple turns. A game ends when one
team reaches 501 points or more.
"""

from .player import Player, BotPlayer
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

    def add_point_one_turn(self, dict_points: dict):
        """Adds points from a completed turn to the team totals.

        Args:
            dict_points: Dictionary mapping player indices to their points for the turn.
        """
        self.team_ns_points += dict_points[0] + dict_points[2]
        self.team_ew_points += dict_points[1] + dict_points[3]

    def new_turn(self) -> dict:
        """Creates and runs a new Turn, returning the resulting points.

        Returns:
            A dictionary mapping player indices to their points for this turn.
        """
        turn = Turn(self.players, self.starting_player_index, Deck())
        return turn.main()

    def reset_player_index(self):
        """Resets all player indices to None at the end of the game.

        Allows Player objects to be reused in a new game without stale state.
        """
        for player in self.players.values():
            player.set_player_index(None)

    def run(self):
        """Runs the game until one team reaches 501 points.

        The starting player rotates by one after each turn. Player indices
        are reset when the game ends.
        """
        while self.team_ew_points < 501 and self.team_ns_points < 501:
            turn_points = self.new_turn()
            self.add_point_one_turn(turn_points)
            self.starting_player_index = (self.starting_player_index + 1) % 4
        self.reset_player_index()


if __name__ == "__main__":
    game = Game([
        BotPlayer(0, 'bot0'),
        BotPlayer(1, 'bot1'),
        BotPlayer(2, 'bot2'),
        BotPlayer(3, 'bot3')
    ])
    game.run()
