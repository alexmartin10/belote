"""une partie (plusieurs tours)
POUR L'INSTANT, MODE SOLO SEULEMENT IMPLEMENTE
"""
from .player import Player, BotPlayer
import random
from .turn import Turn
from .deck import Deck

class Game:
    def __init__(self, players_list: list[Player]):
        for i, player in enumerate(players_list):
            player.set_player_index(i)
        self.players = {
            player.index: player for player in players_list
        }
        self.team_ns_points = 0
        self.team_ew_points = 0
        self.starting_player_index = random.choice([0, 1, 2, 3])

    def add_point_one_turn(self, dict_points):
        self.team_ns_points += dict_points[0] + dict_points[2]
        self.team_ew_points += dict_points[1] + dict_points[3]

    def new_turn(self):
        turn = Turn(
            self.players,
            self.starting_player_index,
            Deck()
        )
        dict_points = turn.main()
        return dict_points
    
    def reset_player_index(self):
        for player in self.players.values():
            player.set_player_index(None)

    def run(self):
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