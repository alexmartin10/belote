from .card import Card, Suit
import numpy as np
from abc import ABC, abstractmethod

class Player(ABC):
    """
    cette classe représente les joueurs
    """
    def __init__(self, id, username):
        self.id = id
        self.username = username

    def set_player_index(self, index: int | None):
        """set the player index for the game"""
        self.index = index
        return index

    def make_hand(self, hand: list[Card]):
        self.hand = hand

    def show_hand(self):
        print(self.hand)

    def cards_of_this_suit_in_hand(self, suit:Suit):
        return [card for card in self.hand if card.suit == suit]

    def playable_cards(self, cards_played:list[Card], trump_suit):
        #1ER CAS SIMPLE : 1ER joueur
        if cards_played == []:
            return self.hand
        
        else:
            first_card_played = cards_played[0]
            suit_to_follow = first_card_played.suit

            #CAS PARTICULIER ATOUT
            if suit_to_follow == trump_suit:
                return self._playable_cards_trump_suit(cards_played, trump_suit)
            
            cards_of_suit_to_follow_in_hand = self.cards_of_this_suit_in_hand(suit_to_follow)
            #SI ON A DES CARTES DE LA COULEUR DEMANDEE ON EST OBLIGES DE METTRE CA
            if len(cards_of_suit_to_follow_in_hand) > 0:
                return cards_of_suit_to_follow_in_hand
            
            #SINON ON PEUT COUPER OU METTRE NIMPORTE QUELLE CARTE
            else:
                trump_cards_in_hand = self.cards_of_this_suit_in_hand(trump_suit)
                if len(trump_cards_in_hand) > 0:
                    return self._playable_cards_trump_suit(cards_played, trump_suit)
                
                else:
                    return self.hand
    
    def _playable_cards_trump_suit(self, cards_played:list[Card], trump_suit):
        """dans le cas ou un atout est joué, ou si l'on doit couper
        vérifier juste que l'on doive monter"""

        trump_cards_in_hand = self.cards_of_this_suit_in_hand(trump_suit)
        if len(trump_cards_in_hand) == 0:
            return self.hand
        
        else:
            #fais la liste des cartes à l'atout jouées, pour dire qu'il faut monter
            #si on peut monter, on le fait, sinon on peut jouer n'importe quel atout
            cards_played_trump_suit = [
                card for card in cards_played if card.suit == trump_suit
            ]
            cards_played_strenght = [
                card.strength(trump_suit) for card in cards_played_trump_suit
            ]
            cards_played_strenght.append(-1) #in case there is no trump card played until now, so
                                             #we can call max at the next line
            higher_cards_in_hand = [
                card for card in trump_cards_in_hand if card.strength(trump_suit) > max(cards_played_strenght)
            ]
            if len(higher_cards_in_hand) > 0:
                return higher_cards_in_hand
            else:
                return trump_cards_in_hand
    
    def remove_card_played(self, card):
        self.hand.remove(card)
    
    @abstractmethod
    def decide_bid(self):
        pass

    @abstractmethod
    def play(self):
        pass


class BotPlayer(Player):
    def __init__(self, id, username):
        super().__init__(id, username)

    def decide_bid(self, trump_card: Card) -> bool:
        points_in_hand = [card.points(trump_card.suit) for card in self.hand]
        return sum(points_in_hand) > 50

    def play(self, player_index_leading, trump_suit, cards_played):
        cards_available_to_play = self.playable_cards(cards_played, trump_suit)
        cards_available_strenght = [
            card.strength(trump_suit) for card in cards_available_to_play
        ]

        if self.is_player_leading_in_my_team(player_index_leading) == True:
            arg = np.argmax(cards_available_strenght)
            card_played = cards_available_to_play[arg]
            return card_played
        else:
            arg = np.argmin(cards_available_strenght)
            card_played = cards_available_to_play[arg]
            return card_played

    def is_player_leading_in_my_team(self, player_index_leading:int):
        return (player_index_leading % 2) == (self.index % 2)
    

class AlwaysTakingBot(Player):
    def decide_bid(self, trump_card):
        return True
    
    def play(self, player_index_leading, trump_suit, cards_played):
        cards_available_to_play = self.playable_cards(cards_played, trump_suit)
        card = cards_available_to_play[0]
        return card
