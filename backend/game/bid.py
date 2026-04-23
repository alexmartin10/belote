from card import Card, Suit

ALL_SUITS = [suit.value for suit in Suit]

class Bid:
    def __init__(self, order, trump_card: Card):
        self.order = order
        self.trump_card = trump_card
        self.trump_suit = trump_card.suit
        self.taker = None
        self.current_bidder = self.order[0]
        self.bid_index = 0
        self.round = 1    

    def _advance_next_bidder(self):
        self.bid_index += 1

        if self.bid_index < 4:
            self.current_bidder = self.order[self.bid_index]
        elif self.bid_index == 4:
            self.round = 2
            self.possible_suits = [s for s in ALL_SUITS if s != self.trump_card.suit.value]
            self.current_bidder = self.order[self.bid_index % 4]
        elif self.bid_index < 8:
            self.current_bidder = self.order[self.bid_index % 4]
        else:
            self.current_bidder = None 
    
    def receive_bid(self, player_index, takes, suit=None):
        if player_index != self.current_bidder:
            raise ValueError("Not this player turn")

        if takes == True:
            if self.round == 2:
                if suit not in self.possible_suits:
                    raise ValueError("Trump suit must be different than the one showed")
                self.trump_suit = suit

            self.taker = player_index
        else:
            self._advance_next_bidder()

        return self.get_state()
    
    def is_bidding_over(self) -> bool:
        return self.taker is not None or self.current_bidder is None

    def get_state(self):
        return {
            'phase': 'bidding',
            'round': self.round,
            'current_bidder': self.current_bidder,
            'trump_suit': self.trump_suit,
            'taker': self.taker,
        }