"""Belote player models.

Defines the abstract Player base class and its concrete implementations.
The engine calls decide_bid() and play() without knowing whether the player
is a bot or a human, following the polymorphism pattern.
"""

from .card import Card, Suit, Rank
from abc import ABC, abstractmethod
from dataclasses import dataclass
import random


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


class Player(ABC):
    """Abstract base class representing a Belote player.

    Defines the interface that all player types must implement.
    Also provides shared logic for hand management and playable card rules.

    Attributes:
        username: Display name of the player.
        index: Position in the current game (0 to 3). Assigned at game start
            via set_player_index() and reset to None after the game ends.
        hand: The player's current cards.
    """

    def __init__(self, username: str):
        """Initializes a Player with a permanent id and username.

        Args:
            username: Display name of the player.
        """
        self.username = username

    def set_player_index(self, index: int | None):
        """Sets the player's position in the current game.

        Args:
            index: Position in the game (0 to 3), or None to reset after game ends.
        """
        self.index = index

    def make_hand(self, hand: list[Card]):
        """Assigns a hand of cards to the player.

        Args:
            hand: List of Card objects to assign as the player's hand.
        """
        self.hand = hand

    def sort_hand(self, trump_suit: Suit):
        """Sorts the player's hand by suit and strength.

        Cards are grouped by suit, with the trump suit placed first.
        Within each suit, cards are sorted from strongest to weakest.
        Uses a stable sort applied in three passes (strength, suit value,
        trump first) as described in the Python sorting documentation.

        Args:
            trump_suit: The current trump suit, placed first in the hand.
        """
        #see https://docs.python.org/3/howto/sorting.html
        #section Sort Stability to understand why it works
        #first, sort by strenght, then by color, then put
        #the trump_suit first.
        if self.hand:
            self.hand.sort(key=lambda card: card.strength(trump_suit), reverse=True)
            self.hand.sort(key=lambda card: card.suit.value)
            self.hand.sort(key=lambda card: card.suit != trump_suit)

    @staticmethod
    def playable_cards(player_hand: list[Card], player_index: int, cards_played: list[Card], 
                       trump_suit: Suit, player_index_leading: int) -> list[Card]:
        """Returns the list of cards the player is legally allowed to play.

        Enforces Belote suit-following, cutting, and trump-climbing rules:
            - If leading the trick, any card can be played.
            - If the led suit is trump, trump rules apply (see _playable_cards_trump_suit).
            - If the player has cards of the led suit, they must play one.
            - If the player cannot follow suit but a teammate is leading, any card can be played.
            - If the player cannot follow suit and no teammate is leading, they must cut with trump.
            - If the player has neither the led suit nor trump, any card can be played.

        Args:
            cards_played: Cards already played in the current trick.
            trump_suit: The current trump suit.
            player_index_leading: Index of the player currently winning the trick.

        Returns:
            A list of legally playable cards.
        """
        if cards_played == []:
            return player_hand

        first_card_played = cards_played[0]
        suit_to_follow = first_card_played.suit

        if suit_to_follow == trump_suit:
            return Player._playable_cards_trump_suit(player_hand, cards_played, trump_suit)

        cards_of_suit_to_follow_in_hand = Player.retrieve_cards_from_container(
            player_hand,
            return_type=list,
            suit=suit_to_follow
        )
        if len(cards_of_suit_to_follow_in_hand) > 0:
            return cards_of_suit_to_follow_in_hand
        
        if Player._are_these_players_in_same_team(player_index, player_index_leading):
        #if we have no card the same color of the first card played but 
        #our mate is leading, we can play any card we want
            return player_hand

        trump_cards_in_hand = Player.retrieve_cards_from_container(
            player_hand,
            return_type=list,
            suit=trump_suit
        )
        if len(trump_cards_in_hand) > 0:
            return Player._playable_cards_trump_suit(player_hand, cards_played, trump_suit)

        return player_hand
    
    @staticmethod
    def _are_these_players_in_same_team(index1: int, index2: int) -> bool:
        """Checks whether the given player is on the same team.

        Teams are (0, 2) and (1, 3).

        Args:
            player_index: Index of the player to check.

        Returns:
            True if the leader is a teammate, False otherwise.
        """
        return (index1 % 2) == (index2 % 2)

    @staticmethod
    def _playable_cards_trump_suit(
            player_hand: list[Card],
            cards_played: list[Card], 
            trump_suit: Suit
            ) -> list[Card]:
        """Returns legal trump cards to play, enforcing the climbing rule.

        When trump is led or the player is cutting, the player must play
        a higher trump than the current highest trump in the trick if possible.
        If they cannot climb, any trump card is allowed.
        If the player has no trump cards at all, any card can be played.

        Args:
            cards_played: Cards already played in the current trick.
            trump_suit: The current trump suit.

        Returns:
            A list of legally playable cards.
        """
        trump_cards_in_hand = Player.retrieve_cards_from_container(
            player_hand,
            return_type=list,
            suit=trump_suit
        )
        if len(trump_cards_in_hand) == 0:
            return player_hand

        cards_played_trump_suit = [
            card for card in cards_played if card.suit == trump_suit
        ]
        cards_played_strength = [
            card.strength(trump_suit) for card in cards_played_trump_suit
        ]
        cards_played_strength.append(-1)  # Ensures max() works when no trump has been played yet

        higher_cards_in_hand = [
            card for card in trump_cards_in_hand
            if card.strength(trump_suit) > max(cards_played_strength)
        ]

        if len(higher_cards_in_hand) > 0:
            return higher_cards_in_hand
        
        return trump_cards_in_hand

    def remove_card_played(self, card: Card):
        """Removes a card from the player's hand after it has been played.

        Called by Trick after validating the card is legal to play.

        Args:
            card: The card to remove from the hand.
        """
        self.hand.remove(card)

    @abstractmethod
    def decide_bid(self, *args, **kargs) -> bool:
        """Decides whether the player takes the contract.

        Args:
            trump_card: The face-up card proposing the trump suit.
            round: The current bidding round (1 or 2).

        Returns:
            A tuple (True,) to accept, (True, suit) to accept with a specific
            suit in round 2, or (False,) to pass.
        """
        pass

    @abstractmethod
    def play(self, *args, **kargs) -> Card:
        """Selects a card to play in the current trick.

        Args:
            player_index_leading: Index of the player currently winning the trick.
            trump_suit: The current trump suit.
            cards_played: Cards already played in the current trick.

        Returns:
            The card the player chooses to play.
        """
        pass

    @staticmethod
    def retrieve_cards_from_container(container, return_type=list, suit=None, rank=None):
        if suit is None and rank is None:
            return return_type(container)

        # Normalize to sets for uniform filtering
        suits = {suit} if isinstance(suit, Suit) else set(suit) if suit is not None else None
        ranks = {rank} if isinstance(rank, Rank) else set(rank) if rank is not None else None

        result = [
            card for card in container
            if (suits is None or card.suit in suits)
            and (ranks is None or card.rank in ranks)
        ]

        return return_type(result)


class MemoryPlayer(Player):
    def __init__(self, username):
        super().__init__(username)
        self._cards_played_in_turn = set()
        
    def decide_bid(self, trump_card: Card, round: int) -> tuple:
        """Takes the contract if the hand is worth more than 50 points.

        In round 1, evaluates the proposed trump suit only. In round 2,
        evaluates all suits and takes with the best one if it exceeds 50 points.
        The trump card itself is included in the point calculation.

        Args:
            trump_card: The face-up card proposing the trump suit.
            round: The current bidding round (1 or 2).

        Returns:
            A tuple (True,) to take with the proposed suit, (True, suit) to
            take with a specific suit in round 2, or (False,) to pass.
        """
        points_in_hand = {
            suit: trump_card.points(suit) + sum([
                card.points(suit) for card in self.hand
            ]) for suit in Suit
        }
        if points_in_hand[trump_card.suit] > 50:
            return (True,)
        else:
            #take the best points total we have un hand
            best_suit, points = sorted(points_in_hand.items(), key=lambda item: item[1], reverse=True)[0]
            if points > 50 and round == 2:
                return (True, best_suit)
            
        return (False,)
    
    def save_trick(self, cards_played: list[Card]):
        self._cards_played_in_turn = self._cards_played_in_turn.union(set(cards_played))

    def play_level_one(
            self,
            player_index_leading: int,
            trump_suit: Suit,
            cards_played: list[Card],
            taker: int,
            non_trump_aces_played: list[Card],
            cards_available_to_play: list[Card]
        ) -> Card:

        cards_available_to_play.sort(key=lambda card: card.strength(trump_suit), reverse=True)

        #Bot Strategy
        #if bot has JACK Trump, play it 
        if Card(Rank.JACK, trump_suit) in cards_available_to_play:
            return Card(Rank.JACK, trump_suit)
        
        #if only one card possible, play it
        if len(cards_available_to_play) == 1:
            return cards_available_to_play[0]
        
        if len(cards_played) == 0:  #bot starts the trick
            #If bot has a trump card, it will be first because of the strenght bonus
            best_card = cards_available_to_play[0]
            #If the taker is in bot's team, play highest trump card if possible
            if (best_card.suit == trump_suit and 
                self._are_these_players_in_same_team(self.index, taker)):
                return best_card
            #taker not in bot's team : forget trumps
            cards_available_to_play = self.retrieve_cards_from_container(
                cards_available_to_play,
                suit=[suit for suit in Suit if suit != trump_suit],
            )
            if not cards_available_to_play: #bot has all the trumps
                return self.playable_cards(self.hand, self.index, cards_played, trump_suit, player_index_leading)[0]
            best_card = cards_available_to_play[0]
            #bot has no trump card or taker not in his team, check if he has Ace
            if best_card.rank == Rank.ACE:
                return best_card
            #bot has no ace, check if he has a ten the color of which the ace has been played
            elif best_card.rank == Rank.TEN and Card(Rank.ACE, best_card.suit) in non_trump_aces_played:
                return best_card
            #else return worst card
            else:
                return cards_available_to_play[-1]
            
        elif len(cards_played) == 3:    #bot ends the trick
            best_card = cards_available_to_play[0]
            #our best card makes us win the trick
            if best_card.strength(trump_suit) > max([
                card.strength(trump_suit) for card in cards_played
                if card.suit in {trump_suit, cards_played[0].suit}
                ]): 
                #condition avoids considering card with better overall strength but 
                #that can not win trick
                return best_card
            #our teammate is leading
            elif self._are_these_players_in_same_team(self.index, player_index_leading):
                return best_card
            else:
                return cards_available_to_play[-1]
        
        else:
            best_card = cards_available_to_play[0]
            #first card is trump, play best if taker is in our team, else worst
            if cards_played[0].suit == trump_suit:
                if self._are_these_players_in_same_team(self.index, taker):
                    return best_card
                else:
                    return cards_available_to_play[-1]
                
            #cut with our best trump if possible
            if best_card.suit == trump_suit:
                return best_card
            
            #unless it'a ten and the ace of same color has not been played,
            #play best card available
            if best_card.strength(trump_suit) > max([
                card.strength(trump_suit) for card in cards_played
                if card.suit in {trump_suit, cards_played[0].suit}
                ]): 
                if best_card.rank == Rank.TEN and Card(Rank.ACE, best_card.suit) in non_trump_aces_played:
                    return best_card
                return cards_available_to_play[-1]
            
            return cards_available_to_play[-1]

    def reset_memory(self):
        self._cards_played_in_turn = set()    


class BotPlayer(MemoryPlayer):
    """A bot player with a basic strategy.

    Bidding strategy: takes the contract if the hand scores more than 50 points
    at the proposed trump suit. In round 2, takes the best available suit if it
    scores more than 50 points.

    Playing strategy: plays the strongest available card when the team is
    winning the trick, the weakest otherwise.

    Attributes:
        username: Display name of the player.
        index: Position in the current game (0 to 3). Assigned at game start
            via set_player_index() and reset to None after the game ends.
        hand: The player's current cards.
        level: Bot's level (between 1-3)
    """

    def __init__(self, username: str, level: int = 1):
        """Initializes a BotPlayer.

        Args:
            username: Display name of the bot player.
        """
        super().__init__(username)
        self._check_level(level)
    
    def _check_level(self, level):
        if level in (1, 2, 3):
            self._level = level
        else:
            raise ValueError("Level must be between 1-3")

    def play(
            self,
            player_index_leading: int,
            trump_suit: Suit,
            cards_played: list[Card],
            taker: int
        ) -> Card:
        """Plays the strongest card if the team leads, the weakest otherwise.

        Args:
            player_index_leading: Index of the player currently winning the trick.
            trump_suit: The current trump suit.
            cards_played: Cards already played in the current trick.

        Returns:
            The selected card to play.
        """
        
        if self._level == 1:
            non_trump_aces_played = self.retrieve_cards_from_container(
                self._cards_played_in_turn,
                return_type=set,
                suit=[suit for suit in Suit if suit != trump_suit],
                rank=Rank.ACE
            )
            cards_available_to_play = self.playable_cards(
                self.hand,
                self.index,
                cards_played,
                trump_suit,
                player_index_leading
            )
            return self.play_level_one(
                player_index_leading,
                trump_suit,
                cards_played,
                taker,
                non_trump_aces_played,
                cards_available_to_play
            )


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
            trick_state: TrickState
        ) -> Card:
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
        pass

    def _mixed_strategy(self):
        """
        Choose the card to play for other players in the simulation.
        Mixed strategy because it chooses randomly or using the
        heuristics definied in the MemomyPlayer class. Used to add
        some novelty in the simulation.
        """
        if random.random() < self._heuristic_play_prob:
            #use heuristics
            pass
        
        else:
            #use random
            pass

class HumanPlayer(Player):
    """A human player whose decisions are provided by the communication layer.

    HumanPlayer does not implement game logic for bidding or playing.
    Decisions are injected externally via the API (FastAPI endpoints).
    The decide_bid method always passes to allow the bidding phase to
    proceed until the API provides the human's actual decision.

    Attributes:
        id: Permanent identifier for the player (e.g. database ID).
        Inherits all other attributes from Player.
    """

    def __init__(self, id, username):
        """Initializes a HumanPlayer with a permanent id and username.

        Args:
            id: Permanent identifier for the player.
            username: Display name of the player.
        """
        super().__init__(username)
        self.id = id
    
    def decide_bid(self, trump_card):
        """Always passes during the automatic bidding phase.

        The human's actual bid is injected by the API via Game.play_bid().
        This method exists only to satisfy the abstract interface and allow
        the engine to advance past the human's turn during initialization.

        Args:
            trump_card: The face-up card proposing the trump suit (unused).

        Returns:
            A tuple (False,) indicating a pass.
        """
        return (False,)
    
    def play(self):
        """Not implemented — human card selection is handled by the API.

        Raises:
            NotImplementedError: Always. Card selection for human players
                is injected via Game.play_card() from the communication layer.
        """
        raise NotImplementedError

class AlwaysTakingBot(Player):
    """A bot that always takes the contract and plays the first legal card.

    Used exclusively in tests to guarantee a taker exists, enabling
    full turn simulation without relying on BotPlayer's bidding heuristic.
    """

    def decide_bid(self, trump_card: Card) -> tuple:
        """Always accepts the contract.

        Args:
            trump_card: The face-up card proposing the trump suit (unused).

        Returns:
            A tuple (True,) indicating acceptance of the contract.
        """
        return (True,)

    def play(self, player_index_leading: int, trump_suit: Suit, cards_played: list[Card]) -> Card:
        """Plays the first legally available card.

        Args:
            player_index_leading: Index of the player currently winning the trick.
            trump_suit: The current trump suit.
            cards_played: Cards already played in the current trick.

        Returns:
            The first card in the list of playable cards.
        """
        return self.playable_cards(self.hand, self.index, cards_played, trump_suit, player_index_leading)[0]
