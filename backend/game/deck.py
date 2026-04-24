"""le jeu de cartes"""

from .card import Card, Suit, Rank
import random

class Deck:
    def __init__(self):
        self.num_players = 4
        self.full_distribution_logic = False #on garde l'ordre des cartes jouées au tour d'avant et on coupe le paquet avant de redistribuer
        self._build()

    def _build(self):
        self.cards = [
            Card(rank, suit)
            for rank in Rank
            for suit in Suit
        ]

    def shuffle(self):
        random.shuffle(self.cards)
    
    def deal_before_bid(self):
        """
        ici on ne s'occupe pas de l'ordre des joueurs, on se contente
        de distribuer des cartes, on assignera les mains aux joueurs 
        correspondants plus tard.
        """
        hands = [[] for _ in range(self.num_players)]

        self.shuffle()

        batch = random.choice([[2, 3], [3, 2]])
        self.next_card_index = 0

        for n in batch:
            for i in range(self.num_players):
                for _ in range(n):
                    hands[i].append(
                        self.cards[self.next_card_index]
                    )
                    self.next_card_index += 1
        
        return hands
    
    def trump_card(self):
        return self.cards[self.next_card_index]

    def deal_after_bid(self, taker_index, hands:list[list]):
        """
        si on utilise cette fonction c'est que quelqu'un a pris
        """
        hands[taker_index].append(self.cards[self.next_card_index])
        self.next_card_index += 1
        n_cards_to_distribute = 3
        for i in range(self.num_players):
            if i == taker_index:
                for _ in range(n_cards_to_distribute - 1): #ce joueur ne recoit que deux cartes
                    hands[i].append(
                        self.cards[self.next_card_index]
                    )
                    self.next_card_index += 1
            else:
                for _ in range(n_cards_to_distribute): #les autres recoivent trois cartes
                    hands[i].append(
                        self.cards[self.next_card_index]
                    )
                    self.next_card_index += 1
        
        return hands
