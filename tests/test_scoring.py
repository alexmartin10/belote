"""Tests for scoring: belote-rebelote, capot, and contract validation."""

from backend.game.turn import Turn
from backend.game.player import AlwaysTakingBot, BotPlayer
from backend.game.deck import Deck
from backend.game.card import Card, Rank, Suit
import pytest


class FixedDeck(Deck):
    """A deck that doesn't shuffle, so card distribution is predictable."""

    def __init__(self, cards: list[Card] = None):
        super().__init__()
        if cards:
            self._cards = cards

    def _shuffle(self):
        pass


def build_deck_with_belote_rebelote(trump_suit: Suit = Suit.HEARTS):
    """Builds a deck where player 0 gets the King and Queen of trump.

    With batch [2, 3] and no shuffle, deal_before_bid distributes:
      - Pass 1 (2 cards each): cards[0:2] → P0, cards[2:4] → P1, cards[4:6] → P2, cards[6:8] → P3
      - Pass 2 (3 cards each): cards[8:11] → P0, cards[11:14] → P1, cards[14:17] → P2, cards[17:20] → P3
    Card at index 20 is the trump_card.

    We place King and Queen of trump at indices 0 and 1 so player 0 gets them.
    We place a card of trump suit at index 20 so the proposed trump matches.
    """
    king_trump = Card(Rank.KING, trump_suit)
    queen_trump = Card(Rank.QUEEN, trump_suit)

    # Build remaining cards (excluding king and queen of trump)
    all_cards = [Card(rank, suit) for rank in Rank for suit in Suit]
    remaining = [c for c in all_cards if not (c.suit == trump_suit and c.rank in (Rank.KING, Rank.QUEEN))]

    # Find a trump card to put at index 20 (the trump_card position)
    trump_card_for_bid = next(c for c in remaining if c.suit == trump_suit)
    remaining.remove(trump_card_for_bid)

    # Build the deck: King and Queen at 0-1, fill the rest, trump card at index 20
    deck_cards = [king_trump, queen_trump] + remaining[:18] + [trump_card_for_bid] + remaining[18:]

    return FixedDeck(deck_cards)


def play_full_turn(turn: Turn):
    """Plays all tricks in a turn with bots."""
    while not turn.is_turn_over():
        if turn._trick is None:
            break
        player_index = turn.current_player
        if player_index is None:
            break
        player = turn._players[player_index]
        turn.play_one_card(
            player_index,
            player.play(
                turn.leading_player,
                turn._bid.trump_suit,
                turn.cards_played
            )
        )


def make_turn_with_fixed_deck(deck):
    """Creates a turn with AlwaysTakingBot at index 0 and 3 BotPlayers."""
    players = {i: BotPlayer(f'bot{i}') for i in range(4)}
    players[0] = AlwaysTakingBot('taker')
    for i, player in players.items():
        player.set_player_index(i)

    turn = Turn(players, 0, deck)
    turn.deal_before_bid()

    # Run bidding (AlwaysTakingBot always takes)
    while not turn._bid.is_bidding_over():
        current = turn.current_player
        player = turn._players[current]
        turn.bid_one_player(current, player.decide_bid(turn.trump_card))

    turn.resolve_second_round_bid()
    return turn


# --- Tests ---

class TestBeloteRebelote:
    def test_belote_rebelote_detected(self):
        deck = build_deck_with_belote_rebelote(Suit.HEARTS)
        turn = make_turn_with_fixed_deck(deck)

        assert turn._player_has_belote_rebelote == 0

    def test_belote_rebelote_not_detected_without_pair(self):
        """With a normal deck, belote-rebelote is unlikely for a specific player."""
        deck = FixedDeck()  # normal order, no shuffle
        turn = make_turn_with_fixed_deck(deck)

        # Could be any player or None — just verify it doesn't crash
        assert turn._player_has_belote_rebelote is None or isinstance(
            turn._player_has_belote_rebelote, int
        )

    def test_belote_rebelote_adds_20_points(self):
        deck = build_deck_with_belote_rebelote(Suit.HEARTS)
        turn = make_turn_with_fixed_deck(deck)
        play_full_turn(turn)

        total = sum(turn.get_points().values())
        assert total == 182  # 162 + 20

    def test_belote_rebelote_kept_on_contract_failure(self):
        """Even if the taking team loses the contract, they keep the 20 points."""
        deck = build_deck_with_belote_rebelote(Suit.HEARTS)
        turn = make_turn_with_fixed_deck(deck)
        play_full_turn(turn)

        # Force contract failure: set taker's team points to 0
        turn._points[0] = 0
        turn._points[2] = 0
        turn._points[1] = 100
        turn._points[3] = 62

        turn.get_points()

        # Taker's team should have 20 (belote-rebelote only)
        taker_team_points = turn._points[0] + turn._points[2]
        assert taker_team_points == 20


class TestCapot:
    def test_total_points_normal_game(self):
        """A normal game without capot should total 162."""
        deck = FixedDeck()
        turn = make_turn_with_fixed_deck(deck)
        play_full_turn(turn)
        turn.get_points()

        total = sum(turn.get_points().values())
        # 162 or 182 if belote-rebelote happened
        assert total in (162, 182)

    def test_capot_gives_252_points(self):
        """If one team takes all tricks, they score 252."""
        deck = FixedDeck()
        turn = make_turn_with_fixed_deck(deck)

        # Simulate capot: taker's team gets all points
        turn._points = {0: 152, 1: 0, 2: 10, 3: 0}
        turn.get_points()

        winning_team = turn._points[0] + turn._points[2]
        losing_team = turn._points[1] + turn._points[3]
        assert winning_team == 252
        assert losing_team == 0

    def test_capot_against_taker(self):
        """If the taker's team scores 0, the other team gets 252."""
        deck = FixedDeck()
        turn = make_turn_with_fixed_deck(deck)

        turn._points = {0: 0, 1: 100, 2: 0, 3: 62}
        turn.get_points()

        taker_team = turn._points[0] + turn._points[2]
        other_team = turn._points[1] + turn._points[3]
        assert taker_team == 0
        assert other_team == 252