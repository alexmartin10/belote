from .card import Card, Suit, Rank
from .player import Player, MemoryPlayer
from dataclasses import dataclass
import random
import time
from copy import deepcopy
from ..utils.utils import argmax


@dataclass
class TrickState:
    hands: dict[int, list[Card]]      # player_index -> cards
    cards_played: list[Card]           # current trick
    starting_player: int
    current_player: int
    leading_player: int
    trump_suit: Suit
    taker: int
    tricks_remaining: int
    points: dict[int, int]            # accumulated this turn


class MCTSBotPlayer(MemoryPlayer):
    ALL_CARDS = [Card(rank, suit) for rank in Rank for suit in Suit]

    def __init__(
            self,
            username,
            n_simulations:int = 500,
            heuristic_play_prob: float = 0.8
            ):
        super().__init__(username)
        self._n_simulations = n_simulations
        self._heuristic_play_prob = heuristic_play_prob
        self._cards_played_in_turn = set()

    def play(
            self,
            trick_state: TrickState,
            time_budget: int = 3
        ) -> Card:

        candidate_cards = Player.playable_cards(
            self.hand,
            self.index,
            trick_state.cards_played,
            trick_state.trump_suit,
            trick_state.leading_player
        )
        if len(candidate_cards) == 1:
            return candidate_cards[0]
        
        start = time.time()
        while time.time() - start < time_budget:
            pass


    def _determinize(self, trick_state: TrickState):
        """distribute all remaining cards to other players"""
        hands = {}
        excluded = self._cards_played_in_turn | set(self.hand) | set(trick_state.cards_played)
        remaining_cards = [card for card in self.ALL_CARDS if card not in excluded]
        random.shuffle(remaining_cards)
        n_cards_to_distribute = len(self.hand)
        n_cards_played = len(trick_state.cards_played)
        distribute_one_less = (n_cards_played == 3)
        next_card_index = 0
        for k in range(1, 4):
            #for players that have already played, distriute one card less
            player_index = (self.index + k) % 4
            end = next_card_index + n_cards_to_distribute - int(distribute_one_less)
            hands[player_index] = remaining_cards[next_card_index : end]
            next_card_index = end
            n_cards_played += 1
            distribute_one_less = (n_cards_played == 3)

        return hands

    def _simulate(self, trick_state: TrickState, candidate_card: Card):
        def get_leader(cards_played: list[Card], trump_suit: Suit, starting_player):
            """Updates the leading player based on the cards played so far.

            Only cards of the led suit or trump suit are considered when computing
            strengths. Cards of other suits are assigned strength 0. The player
            with the highest strength card wins the trick.
            """
            suit_to_follow = cards_played[0].suit
            strengths = [card.strength(trump_suit) 
                        if (card.suit == suit_to_follow or card.suit == trump_suit) 
                        else 0 for card in cards_played]
            try:
                return (starting_player + argmax(strengths)) % 4
            except ValueError:
                #argmax raises ValueError if strenghts is empty
                return starting_player


        ts = deepcopy(trick_state) #ts stands for trick_state. copy is made because it will be modified

        #adding candidate card to cards played and removing it from player's hand
        ts.cards_played.append(candidate_card)
        ts.hands[ts.current_player].remove(candidate_card)

        #advancing player
        ts.current_player += 1
        ts.current_player %= 4

        while ts.tricks_remaining > 0:
            ts.leading_player = get_leader(
                ts.cards_played,
                ts.trump_suit,
                ts.starting_player
            )
            #reprendre chaque pli quand on a joué 4 cartes
            if len(ts.cards_played) == 4:
                #fin du trick
                points = sum([card.points(ts.trump_suit) for card in ts.cards_played])
                ts.points[ts.leading_player] += points
                ts.starting_player = ts.leading_player
                ts.cards_played = []
                ts.tricks_remaining -= 1
            
            else:
                card_chosen = self._mixed_strategy(ts.current_player, ts)
                ts.hands[ts.current_player].remove(card_chosen)
                ts.cards_played.append(card_chosen)
                ts.current_player += 1
                ts.current_player %= 4


    def _mixed_strategy(
            self,
            player_index,
            trick_state: TrickState
        ):
        """
        Choose the card to play for other players in the simulation.
        Mixed strategy because it chooses randomly or using the
        heuristics definied in the MemomyPlayer class. Used to add
        some novelty in the simulation.

        Args: possible_cards : list of cards that are legal to play
            for the current player
            trick_state : contains all arguments to give to heuristic
        """
        player_hand = trick_state.hands[player_index]

        if random.random() < self._heuristic_play_prob:
            #use heuristics
            non_trump_aces_played = self.retrieve_cards_from_container(
                self._cards_played_in_turn,
                return_type=set,
                suit=[suit for suit in Suit if suit != trick_state.trump_suit],
                rank=Rank.ACE
            )
            return self.play_level_one(
                player_hand,
                player_index,
                trick_state.leading_player,
                trick_state.trump_suit,
                trick_state.cards_played,
                trick_state.taker,
                non_trump_aces_played
            )
        
        else:
            #choose randomly
            possible_cards = Player.playable_cards(
                player_hand,
                player_index,
                trick_state.cards_played,
                trick_state.trump_suit,
                trick_state.leading_player
            )
            return random.choice(possible_cards)