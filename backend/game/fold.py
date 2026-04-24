from .card import Suit
from .player import Player

import numpy as np

ALL_SUITS = [suit.value for suit in Suit]

class Fold:
    def __init__(self, players: dict[int: Player], starting_player_index, trump_suit: Suit):
        self.current_player = starting_player_index
        self.starting_player = starting_player_index
        self.trump_suit = trump_suit
        self.cards_played = []
        self.players = players
        self.leading_player = starting_player_index
        self.points = None

    def receive_card(self, player_index, card):
        if player_index != self.current_player:
            raise ValueError("Not this player's turn")
        
        player = self.players[player_index]
        if card not in player.playable_cards(self.cards_played, self.trump_suit):
            raise ValueError("Can't play this card")
        else:
            self.cards_played.append(card)
            self._advance_next_player()
        
        return self.get_state()
    
    def _advance_next_player(self):
        self.current_player += 1
        self.current_player = self.current_player % 4
        self._get_leader()

        #when everyone played
        if self.current_player == self.starting_player:
            self.current_player = None

            self._count_points()
    
    def get_state(self):
        return {
            'current_player': self.current_player,
            'cards_played': self.cards_played,
            'leading_player': self.leading_player,
            'points': self.points
        }
    
    def is_fold_over(self):
        return self.current_player == None
    
    def _get_leader(self):
        """return the index of the winner"""
        strenghts = [card.strength(self.trump_suit) for card in self.cards_played]
        arg = np.argmax(strenghts)
        self.leading_player = (self.starting_player + arg) % 4
    
    def _count_points(self):
        self.points = sum([card.points(self.trump_suit) for card in self.cards_played])