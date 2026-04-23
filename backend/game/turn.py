"""la logique d'un tour (cartes jouées, points, plis)
fold = pli
turn = manche
"""

from card import Card, Suit, Rank
from deck import Deck
from player import BotPlayer
from fold import Fold
import numpy as np
from bid import Bid

class Turn:
    def __init__(self, players: list[BotPlayer], starting_player_index, deck:Deck):
        self.players = {
            player.index: player for player in players
        }
        self.starting_player_index = starting_player_index
        self.deck = deck
        self.order = [
            (starting_player_index + k) % 4 for k in range(4)
        ]
        self.points = { #key=index, value=points
            0: 0,
            1: 0,
            2: 0,
            3: 0
        }

    def deal(self):
        hands_before_bid = self.deck.deal_before_bid()
        self.trump_card = self.deck.trump_card()
        self.bid = Bid(self.order, self.trump_card)
        for index, hand in zip(self.order, hands_before_bid):
            player = self.players[index]
            player.make_hand(hand)
        while not self.bid.is_bidding_over():
            current_player = self.players[self.bid.current_bidder]
            self.bid_state = self.bid.receive_bid(
                current_player.index,
                current_player.decide_bid(self.bid.trump_card),
                suit=None
            )
        if self.bid.current_bidder is None:
            self.new_turn()
        else:
            self.play_folds()
    
    def new_turn(self):
        raise NotImplementedError

    def play_folds(self):
        starting_player = self.starting_player_index
        for _ in range(8):
            fold = Fold(
                self.players,
                starting_player,
                self.bid.trump_suit
            )
            while not fold.is_fold_over():
                player = self.players[fold.current_player]
                fold_state = fold.receive_card(
                    player_index = fold.current_player,
                    card = player.play(
                        player_index_leading=fold.leading_player,
                        trump_suit=self.trump_card.suit
                    )
                )
            self.points[fold.leading_player] += fold.points
            starting_player = fold.leading_player
        self.points[fold.leading_player] += 10 #10 de der
        
    def _check_contract(self):
        points_team_taking_contract = self.points[self.bid.taker] + self.points[(self.bid.taker + 2) % 4]
        return points_team_taking_contract > 81

    def get_points(self):
        if self._check_contract():
            pass
        else:
            self.points = {
                self.taker: 0,
                (self.taker + 1) % 4: 162,
                (self.taker + 2) % 4: 0,
                (self.taker + 3) % 4: 0
            }
    
    def main(self):
        self.deal()
        if self.bid.taker is not None:
            self.play_folds()
            self.get_points()
        
        return self.points