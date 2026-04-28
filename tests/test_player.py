from backend.game.player import BotPlayer, AlwaysTakingBot
from backend.game.card import Card, Rank, Suit
import pytest


def same_elements(a, b):
    """Returns True if both lists contain the same elements regardless of order."""
    if len(a) != len(b):
        return False
    remaining = list(b)
    for x in a:
        if x in remaining:
            remaining.remove(x)
        else:
            return False
    return True


@pytest.fixture
def basic_bot():
    """A BotPlayer (index 0) holding 10♠, J♠, A♥, Q♥."""
    player = BotPlayer('bot')
    player.set_player_index(0)
    player.make_hand([
        Card(Rank.TEN, Suit.SPADES),
        Card(Rank.JACK, Suit.SPADES),
        Card(Rank.ACE, Suit.HEARTS),
        Card(Rank.QUEEN, Suit.HEARTS),
    ])
    return player


@pytest.fixture
def taker_bot():
    """An AlwaysTakingBot (index 0) holding 10♠, J♠, A♥, Q♥."""
    player = AlwaysTakingBot('taker')
    player.set_player_index(0)
    player.make_hand([
        Card(Rank.TEN, Suit.SPADES),
        Card(Rank.JACK, Suit.SPADES),
        Card(Rank.ACE, Suit.HEARTS),
        Card(Rank.QUEEN, Suit.HEARTS),
    ])
    return player


# ---------------------------------------------------------------------------
# BotPlayer — playable_cards
# ---------------------------------------------------------------------------

def test_bot_playable_cards_must_climb_when_trump_led_higher(basic_bot: BotPlayer):
    cards_played = [Card(Rank.JACK, Suit.HEARTS), Card(Rank.SEVEN, Suit.DIAMONDS)]
    assert same_elements(
        basic_bot.playable_cards(cards_played, Suit.HEARTS),
        [Card(Rank.QUEEN, Suit.HEARTS), Card(Rank.ACE, Suit.HEARTS)]
    )


def test_bot_playable_cards_must_climb_when_trump_led_lower(basic_bot: BotPlayer):
    cards_played = [Card(Rank.EIGHT, Suit.HEARTS)]
    assert same_elements(
        basic_bot.playable_cards(cards_played, Suit.HEARTS),
        [Card(Rank.QUEEN, Suit.HEARTS), Card(Rank.ACE, Suit.HEARTS)]
    )


def test_bot_playable_cards_must_climb_when_trump_led_between(basic_bot: BotPlayer):
    cards_played = [Card(Rank.TEN, Suit.HEARTS)]
    assert basic_bot.playable_cards(cards_played, Suit.HEARTS) == [Card(Rank.ACE, Suit.HEARTS)]


def test_bot_playable_cards_must_cut_when_no_suit_to_follow(basic_bot: BotPlayer):
    cards_played = [Card(Rank.JACK, Suit.CLUBS)]
    assert same_elements(
        basic_bot.playable_cards(cards_played, Suit.HEARTS),
        [Card(Rank.QUEEN, Suit.HEARTS), Card(Rank.ACE, Suit.HEARTS)]
    )


def test_bot_playable_cards_must_climb_when_cutting(basic_bot: BotPlayer):
    cards_played = [Card(Rank.JACK, Suit.CLUBS), Card(Rank.EIGHT, Suit.HEARTS)]
    assert same_elements(
        basic_bot.playable_cards(cards_played, Suit.HEARTS),
        [Card(Rank.QUEEN, Suit.HEARTS), Card(Rank.ACE, Suit.HEARTS)]
    )


def test_bot_playable_cards_cannot_climb_when_cutting(basic_bot: BotPlayer):
    cards_played = [Card(Rank.JACK, Suit.CLUBS), Card(Rank.NINE, Suit.HEARTS)]
    assert same_elements(
        basic_bot.playable_cards(cards_played, Suit.HEARTS),
        [Card(Rank.QUEEN, Suit.HEARTS), Card(Rank.ACE, Suit.HEARTS)]
    )


def test_bot_playable_cards_any_card_when_leading(basic_bot: BotPlayer):
    assert same_elements(basic_bot.playable_cards([], Suit.HEARTS), basic_bot.hand)


def test_bot_playable_cards_any_trump_when_cannot_climb(basic_bot: BotPlayer):
    cards_played = [Card(Rank.JACK, Suit.HEARTS), Card(Rank.NINE, Suit.HEARTS)]
    assert same_elements(
        basic_bot.playable_cards(cards_played, Suit.HEARTS),
        [Card(Rank.ACE, Suit.HEARTS), Card(Rank.QUEEN, Suit.HEARTS)]
    )


def test_bot_playable_cards_any_card_when_no_trump_in_hand(basic_bot: BotPlayer):
    cards_played = [Card(Rank.JACK, Suit.CLUBS), Card(Rank.NINE, Suit.CLUBS)]
    assert same_elements(basic_bot.playable_cards(cards_played, Suit.CLUBS), basic_bot.hand)


def test_bot_playable_cards_any_card_when_cannot_cut(basic_bot: BotPlayer):
    cards_played = [Card(Rank.JACK, Suit.CLUBS), Card(Rank.NINE, Suit.CLUBS)]
    assert same_elements(basic_bot.playable_cards(cards_played, Suit.DIAMONDS), basic_bot.hand)


# ---------------------------------------------------------------------------
# BotPlayer — play
# ---------------------------------------------------------------------------

def test_bot_plays_strongest_card_when_team_leads(basic_bot: BotPlayer):
    cards_played = [Card(Rank.ACE, Suit.SPADES), Card(Rank.QUEEN, Suit.SPADES)]
    card = basic_bot.play(player_index_leading=2, trump_suit=Suit.HEARTS, cards_played=cards_played)
    assert card == Card(Rank.TEN, Suit.SPADES)


def test_bot_plays_weakest_card_when_team_does_not_lead(basic_bot: BotPlayer):
    cards_played = [Card(Rank.ACE, Suit.SPADES), Card(Rank.QUEEN, Suit.SPADES), Card(Rank.SEVEN, Suit.SPADES)]
    card = basic_bot.play(player_index_leading=1, trump_suit=Suit.HEARTS, cards_played=cards_played)
    assert card == Card(Rank.JACK, Suit.SPADES)


def test_bot_played_card_is_removed_from_hand(basic_bot: BotPlayer):
    hand_size_before = len(basic_bot.hand)
    card = basic_bot.play(player_index_leading=2, trump_suit=Suit.HEARTS, cards_played=[])
    basic_bot.remove_card_played(card)
    assert len(basic_bot.hand) == hand_size_before - 1
    assert card not in basic_bot.hand


# ---------------------------------------------------------------------------
# AlwaysTakingBot — playable_cards (same rules as BotPlayer)
# ---------------------------------------------------------------------------

def test_taker_playable_cards_must_climb_when_trump_led_higher(taker_bot: AlwaysTakingBot):
    cards_played = [Card(Rank.JACK, Suit.HEARTS), Card(Rank.SEVEN, Suit.DIAMONDS)]
    assert same_elements(
        taker_bot.playable_cards(cards_played, Suit.HEARTS),
        [Card(Rank.QUEEN, Suit.HEARTS), Card(Rank.ACE, Suit.HEARTS)]
    )


def test_taker_playable_cards_must_climb_when_trump_led_lower(taker_bot: AlwaysTakingBot):
    cards_played = [Card(Rank.EIGHT, Suit.HEARTS)]
    assert same_elements(
        taker_bot.playable_cards(cards_played, Suit.HEARTS),
        [Card(Rank.QUEEN, Suit.HEARTS), Card(Rank.ACE, Suit.HEARTS)]
    )


def test_taker_playable_cards_must_climb_when_trump_led_between(taker_bot: AlwaysTakingBot):
    cards_played = [Card(Rank.TEN, Suit.HEARTS)]
    assert taker_bot.playable_cards(cards_played, Suit.HEARTS) == [Card(Rank.ACE, Suit.HEARTS)]


def test_taker_playable_cards_must_cut_when_no_suit_to_follow(taker_bot: AlwaysTakingBot):
    cards_played = [Card(Rank.JACK, Suit.CLUBS)]
    assert same_elements(
        taker_bot.playable_cards(cards_played, Suit.HEARTS),
        [Card(Rank.QUEEN, Suit.HEARTS), Card(Rank.ACE, Suit.HEARTS)]
    )


def test_taker_playable_cards_must_climb_when_cutting(taker_bot: AlwaysTakingBot):
    cards_played = [Card(Rank.JACK, Suit.CLUBS), Card(Rank.EIGHT, Suit.HEARTS)]
    assert same_elements(
        taker_bot.playable_cards(cards_played, Suit.HEARTS),
        [Card(Rank.QUEEN, Suit.HEARTS), Card(Rank.ACE, Suit.HEARTS)]
    )


def test_taker_playable_cards_cannot_climb_when_cutting(taker_bot: AlwaysTakingBot):
    cards_played = [Card(Rank.JACK, Suit.CLUBS), Card(Rank.NINE, Suit.HEARTS)]
    assert same_elements(
        taker_bot.playable_cards(cards_played, Suit.HEARTS),
        [Card(Rank.QUEEN, Suit.HEARTS), Card(Rank.ACE, Suit.HEARTS)]
    )


def test_taker_playable_cards_any_card_when_leading(taker_bot: AlwaysTakingBot):
    assert same_elements(taker_bot.playable_cards([], Suit.HEARTS), taker_bot.hand)


def test_taker_playable_cards_any_card_when_no_trump_in_hand(taker_bot: AlwaysTakingBot):
    cards_played = [Card(Rank.JACK, Suit.CLUBS), Card(Rank.NINE, Suit.CLUBS)]
    assert same_elements(taker_bot.playable_cards(cards_played, Suit.CLUBS), taker_bot.hand)


def test_taker_playable_cards_any_card_when_cannot_cut(taker_bot: AlwaysTakingBot):
    cards_played = [Card(Rank.JACK, Suit.CLUBS), Card(Rank.NINE, Suit.CLUBS)]
    assert same_elements(taker_bot.playable_cards(cards_played, Suit.DIAMONDS), taker_bot.hand)