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


def test_sort_hand_trump_suit_at_the_beginning(basic_bot: BotPlayer):
    basic_bot.sort_hand(Suit.SPADES)
    assert basic_bot.hand == [
        Card(Rank.JACK, Suit.SPADES),
        Card(Rank.TEN, Suit.SPADES),
        Card(Rank.ACE, Suit.HEARTS),
        Card(Rank.QUEEN, Suit.HEARTS),
    ]

def test_sort_hand_trump_suit_at_the_end(basic_bot: BotPlayer):
    basic_bot.sort_hand(Suit.HEARTS)
    assert basic_bot.hand == [
        Card(Rank.ACE, Suit.HEARTS),
        Card(Rank.QUEEN, Suit.HEARTS),
        Card(Rank.TEN, Suit.SPADES),
        Card(Rank.JACK, Suit.SPADES)
    ]

def test_sort_hand_no_trump_suit(basic_bot: BotPlayer):
    """When we have no card of trump suit in hand, 
    the cards are automatically sorted in this suit order :
    ['♠', '♣', '♥', '♦']. That's how the sort method naturally
    sorts all suits."""
    basic_bot.sort_hand(Suit.DIAMONDS)
    assert basic_bot.hand == [
        Card(Rank.TEN, Suit.SPADES),
        Card(Rank.JACK, Suit.SPADES),
        Card(Rank.ACE, Suit.HEARTS),
        Card(Rank.QUEEN, Suit.HEARTS),
    ]

def test_bot_takes_when_total_points_over_50():
    player = BotPlayer('bot')
    player.set_player_index(0)
    #10+20+11+14 = 55 points when trump suit is spades
    player.make_hand([
        Card(Rank.TEN, Suit.SPADES),
        Card(Rank.JACK, Suit.SPADES),
        Card(Rank.ACE, Suit.SPADES),
        Card(Rank.NINE, Suit.SPADES),
    ])
    assert player.decide_bid(Card(Rank.SEVEN, Suit.SPADES), round=1) == (True,)


def test_bot_takes_when_total_points_over_50_with_shown_card():
    player = BotPlayer('bot')
    player.set_player_index(0)
    #10+20+11+14 = 55 points when trump suit is spades
    player.make_hand([
        Card(Rank.TEN, Suit.SPADES),
        Card(Rank.JACK, Suit.SPADES),
        Card(Rank.SEVEN, Suit.SPADES),
        Card(Rank.NINE, Suit.SPADES),
    ])
    assert player.decide_bid(Card(Rank.ACE, Suit.SPADES), round=1) == (True,)


def test_bot_takes_in_round_2():
    player = BotPlayer('bot')
    player.set_player_index(0)
    #10+20+14 = 44 points when trump suit is spades, +11 with the card shown
    player.make_hand([
        Card(Rank.TEN, Suit.SPADES),
        Card(Rank.JACK, Suit.SPADES),
        Card(Rank.SEVEN, Suit.SPADES),
        Card(Rank.NINE, Suit.SPADES),
    ])
    assert player.decide_bid(Card(Rank.ACE, Suit.HEARTS), round=2) == (True, Suit.SPADES)

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