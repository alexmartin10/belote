"""une partie (plusieurs tours)
POUR L'INSTANT, MODE SOLO SEULEMENT IMPLEMENTE
"""
from player import UserPlayer, BotPlayer
import random
from turn import Turn
from deck import Deck

class Game:
    def __init__(self):
        pass

    def new_game(self):
        self.player_south = UserPlayer(index=0)
        self.player_west = BotPlayer(index=1)
        self.player_north = BotPlayer(index=2)
        self.player_east = BotPlayer(index=3)
        self.players_list = [
            self.player_south,
            self.player_west,
            self.player_north,
            self.player_east
        ]
        self.team_ns_points = 0
        self.team_ew_points = 0
        self.starting_player_index = random.choice([0, 1, 2, 3])

    def add_point_one_turn(self, dict_points):
        self.team_ns_points += dict_points[0] + dict_points[2]
        self.team_ew_points += dict_points[1] + dict_points[3]

    def new_turn(self):
        turn = Turn(
            self.players_list,
            self.starting_player_index,
            Deck()
        )
        dict_points = turn.main()
        return dict_points


    def run(self):
        self.new_game()
        while self.team_ew_points < 501 and self.team_ns_points < 501:
            turn_points = self.new_turn()
            self.add_point_one_turn(turn_points)


if __name__ == "__main__":
    game = Game()
    game.run()