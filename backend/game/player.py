"""Belote player models.

Defines the abstract Player base class and its concrete implementations.
The engine calls decide_bid() and play() without knowing whether the player
is a bot or a human, following the polymorphism pattern.
"""

from .card import Card, Suit
from ..utils.utils import argmin, argmax
from abc import ABC, abstractmethod


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

        Returns:
            The index that was set.
        """
        self.index = index

    def make_hand(self, hand: list[Card]):
        """Assigns a hand of cards to the player.

        Args:
            hand: List of Card objects to assign as the player's hand.
        """
        self.hand = hand

    def sort_hand(self, trump_suit: Suit):
        #see https://docs.python.org/3/howto/sorting.html
        #section Sort Stability to understand why it works
        #first, sort by strenght, then by color, then put
        #the trump_suit first.
        if self.hand:
            self.hand.sort(key=lambda card: card.strength(trump_suit), reverse=True)
            self.hand.sort(key=lambda card: card.suit.value)
            self.hand.sort(key=lambda card: card.suit != trump_suit)

    def _cards_of_this_suit_in_hand(self, suit: Suit) -> list[Card]:
        """Returns all cards of a given suit in the player's hand.

        Args:
            suit: The suit to filter by.

        Returns:
            A list of cards matching the given suit.
        """
        return [card for card in self.hand if card.suit == suit]

    def playable_cards(self, cards_played: list[Card], trump_suit: Suit, 
                       player_index_leading: int) -> list[Card]:
        """Returns the list of cards the player is legally allowed to play.

        Enforces Belote suit-following, cutting, and trump-climbing rules:
            - If leading the trick, any card can be played.
            - If the led suit is trump, trump rules apply (see _playable_cards_trump_suit).
            - If the player has cards of the led suit, they must play one.
            - If the player cannot follow suit but has trump cards, they must cut.
            - If the player has neither, any card can be played.

        Args:
            cards_played: Cards already played in the current trick.
            trump_suit: The current trump suit.

        Returns:
            A list of legally playable cards.
        """
        if cards_played == []:
            return self.hand

        first_card_played = cards_played[0]
        suit_to_follow = first_card_played.suit

        if suit_to_follow == trump_suit:
            return self._playable_cards_trump_suit(cards_played, trump_suit)

        cards_of_suit_to_follow_in_hand = self._cards_of_this_suit_in_hand(suit_to_follow)
        if len(cards_of_suit_to_follow_in_hand) > 0:
            return cards_of_suit_to_follow_in_hand
        
        if self._is_player_leading_in_my_team(player_index_leading):
        #if we have no card the same color of the first card played but 
        #our mate is leading, we can play any card we want
            return self.hand

        trump_cards_in_hand = self._cards_of_this_suit_in_hand(trump_suit)
        if len(trump_cards_in_hand) > 0:
            return self._playable_cards_trump_suit(cards_played, trump_suit)

        return self.hand
    
    def _is_player_leading_in_my_team(self, player_index_leading: int) -> bool:
        """Checks whether the current trick leader is on the same team.

        Teams are (0, 2) and (1, 3).

        Args:
            player_index_leading: Index of the player currently winning the trick.

        Returns:
            True if the leader is a teammate, False otherwise.
        """
        return (player_index_leading % 2) == (self.index % 2)

    def _playable_cards_trump_suit(self, cards_played: list[Card], trump_suit: Suit) -> list[Card]:
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
        trump_cards_in_hand = self._cards_of_this_suit_in_hand(trump_suit)
        if len(trump_cards_in_hand) == 0:
            return self.hand

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

        Returns:
            True to accept the contract, False to pass.
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


class BotPlayer(Player):
    """A bot player with a basic strategy.

    Bidding strategy: takes the contract if the hand scores more than 50 points
    at the proposed trump suit.

    Playing strategy: plays the strongest available card when the team is
    winning the trick, the weakest otherwise.

    Attributes:
        Inherits all attributes from Player.
    """

    def __init__(self, username: str):
        """Initializes a BotPlayer.

        Args:
            id: Permanent identifier for the player.
            username: Display name of the player.
        """
        super().__init__(username)

    def decide_bid(self, trump_card: Card, round: int) -> bool:
        """Takes the contract if the hand is worth more than 50 points.

        Args:
            trump_card: The face-up card proposing the trump suit.

        Returns:
            True if the hand total exceeds 50 points, False otherwise.
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

    def play(self, player_index_leading: int, trump_suit: Suit, cards_played: list[Card]) -> Card:
        """Plays the strongest card if the team leads, the weakest otherwise.

        Args:
            player_index_leading: Index of the player currently winning the trick.
            trump_suit: The current trump suit.
            cards_played: Cards already played in the current trick.

        Returns:
            The selected card to play.
        """
        cards_available_to_play = self.playable_cards(cards_played, trump_suit, player_index_leading)
        cards_available_strength = [
            card.strength(trump_suit) for card in cards_available_to_play
        ]

        if self._is_player_leading_in_my_team(player_index_leading):
            arg = argmax(cards_available_strength)
        else:
            arg = argmin(cards_available_strength)

        return cards_available_to_play[arg]


class HumanPlayer(Player):
    def __init__(self, id, username):
        super().__init__(username)
        self.id = id
    
    def decide_bid(self, trump_card):
        return (False,)
    
    def play(self):
        raise NotImplementedError

class AlwaysTakingBot(Player):
    """A bot that always takes the contract and plays the first legal card.

    Used exclusively in tests to guarantee a taker exists, enabling
    full turn simulation without relying on BotPlayer's bidding heuristic.
    """

    def decide_bid(self, trump_card: Card) -> bool:
        """Always accepts the contract.

        Args:
            trump_card: The face-up card proposing the trump suit.

        Returns:
            Always True.
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
        return self.playable_cards(cards_played, trump_suit, player_index_leading)[0]
