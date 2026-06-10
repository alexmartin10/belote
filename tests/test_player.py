from backend.game.player import BotPlayer, AlwaysTakingBot, Player
from backend.game.card import Card, Rank, Suit
from backend.game.deck import Deck
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
        basic_bot.playable_cards(basic_bot.hand, basic_bot.index, cards_played, Suit.HEARTS, 2),
        [Card(Rank.QUEEN, Suit.HEARTS), Card(Rank.ACE, Suit.HEARTS)],
    )


def test_bot_playable_cards_must_climb_when_trump_led_lower(basic_bot: BotPlayer):
    cards_played = [Card(Rank.EIGHT, Suit.HEARTS)]
    assert same_elements(
        basic_bot.playable_cards(basic_bot.hand, basic_bot.index, cards_played, Suit.HEARTS, 3),
        [Card(Rank.QUEEN, Suit.HEARTS), Card(Rank.ACE, Suit.HEARTS)]
    )


def test_bot_playable_cards_must_climb_when_trump_led_between(basic_bot: BotPlayer):
    cards_played = [Card(Rank.TEN, Suit.HEARTS)]
    assert basic_bot.playable_cards(basic_bot.hand, basic_bot.index, cards_played, Suit.HEARTS, 3) == [Card(Rank.ACE, Suit.HEARTS)]


def test_bot_playable_cards_must_cut_when_no_suit_to_follow(basic_bot: BotPlayer):
    cards_played = [Card(Rank.JACK, Suit.CLUBS)]
    assert same_elements(
        basic_bot.playable_cards(basic_bot.hand, basic_bot.index, cards_played, Suit.HEARTS, 3),
        [Card(Rank.QUEEN, Suit.HEARTS), Card(Rank.ACE, Suit.HEARTS)]
    )


def test_bot_playable_cards_must_climb_when_cutting(basic_bot: BotPlayer):
    cards_played = [Card(Rank.JACK, Suit.CLUBS), Card(Rank.EIGHT, Suit.HEARTS)]
    assert same_elements(
        basic_bot.playable_cards(basic_bot.hand, basic_bot.index, cards_played, Suit.HEARTS, 3),
        [Card(Rank.QUEEN, Suit.HEARTS), Card(Rank.ACE, Suit.HEARTS)]
    )


def test_bot_playable_cards_cannot_climb_when_cutting(basic_bot: BotPlayer):
    cards_played = [Card(Rank.JACK, Suit.CLUBS), Card(Rank.NINE, Suit.HEARTS)]
    assert same_elements(
        basic_bot.playable_cards(basic_bot.hand, basic_bot.index, cards_played, Suit.HEARTS, 3),
        [Card(Rank.QUEEN, Suit.HEARTS), Card(Rank.ACE, Suit.HEARTS)]
    )


def test_bot_playable_cards_any_card_when_leading(basic_bot: BotPlayer):
    assert same_elements(basic_bot.playable_cards(basic_bot.hand, basic_bot.index, [], Suit.HEARTS, 0), basic_bot.hand)


def test_bot_playable_cards_any_trump_when_cannot_climb(basic_bot: BotPlayer):
    cards_played = [Card(Rank.JACK, Suit.HEARTS), Card(Rank.NINE, Suit.HEARTS)]
    assert same_elements(
        basic_bot.playable_cards(basic_bot.hand, basic_bot.index, cards_played, Suit.HEARTS, 2),
        [Card(Rank.ACE, Suit.HEARTS), Card(Rank.QUEEN, Suit.HEARTS)]
    )


def test_bot_playable_cards_any_card_when_no_trump_in_hand(basic_bot: BotPlayer):
    cards_played = [Card(Rank.JACK, Suit.CLUBS), Card(Rank.NINE, Suit.CLUBS)]
    assert same_elements(basic_bot.playable_cards(basic_bot.hand, basic_bot.index, cards_played, Suit.CLUBS, 2), basic_bot.hand)


def test_bot_playable_cards_any_card_when_cannot_cut(basic_bot: BotPlayer):
    cards_played = [Card(Rank.JACK, Suit.CLUBS), Card(Rank.NINE, Suit.CLUBS)]
    assert same_elements(basic_bot.playable_cards(basic_bot.hand, basic_bot.index, cards_played, Suit.DIAMONDS, 2), basic_bot.hand)


def test_bot_playable_cards_when_teammate_holds(basic_bot: BotPlayer):
    cards_played = [Card(Rank.JACK, Suit.CLUBS), Card(Rank.NINE, Suit.CLUBS)]
    assert same_elements(basic_bot.playable_cards(basic_bot.hand, basic_bot.index, cards_played, Suit.HEARTS, 2), basic_bot.hand)


# ---------------------------------------------------------------------------
# BotPlayer — play
# ---------------------------------------------------------------------------

def test_bot_played_card_is_removed_from_hand(basic_bot: BotPlayer):
    hand_size_before = len(basic_bot.hand)
    card = basic_bot.play( player_index_leading=2, trump_suit=Suit.HEARTS, cards_played=[], taker=0)
    basic_bot.remove_card_played(card)
    assert len(basic_bot.hand) == hand_size_before - 1
    assert card not in basic_bot.hand

#starting position

def test_level_one_bot_starts_with_jack_trump_when_teammate_took(basic_bot: BotPlayer):
    card = basic_bot.play( 
        player_index_leading=0,
        trump_suit=Suit.SPADES,
        cards_played=[],
        taker=2
    )
    assert card == Card(Rank.JACK, Suit.SPADES)


def test_level_one_bot_starts_with_jack_trump_when_opponent_took(basic_bot: BotPlayer):
    card = basic_bot.play( 
        player_index_leading=0,
        trump_suit=Suit.SPADES,
        cards_played=[],
        taker=1
    )
    assert card == Card(Rank.JACK, Suit.SPADES)


def test_level_one_bot_starts_with_best_trump_if_teammate_took(basic_bot: BotPlayer):
    card = basic_bot.play( 
        player_index_leading=0,
        trump_suit=Suit.HEARTS,
        cards_played=[],
        taker=2
    )
    assert card == Card(Rank.ACE, Suit.HEARTS)


def test_level_one_bot_starts_with_ace_if_no_trump_and_teammate_took(basic_bot: BotPlayer):
    card = basic_bot.play( 
        player_index_leading=0,
        trump_suit=Suit.DIAMONDS,
        cards_played=[],
        taker=2
    )
    assert card == Card(Rank.ACE, Suit.HEARTS)


def test_level_one_bot_starts_with_ace_if_opponent_took():
    player = BotPlayer('0')
    player.set_player_index(0)
    player.make_hand([Card(Rank.ACE, Suit.HEARTS), Card(Rank.NINE, Suit.DIAMONDS)])
    card = player.play(
        player_index_leading=0,
        trump_suit=Suit.DIAMONDS,
        cards_played=[],
        taker=1
    )
    assert card == Card(Rank.ACE, Suit.HEARTS)


def test_level_one_bot_starts_with_ten_if_opponent_took_and_ace_has_fallen(basic_bot: BotPlayer):
    basic_bot.save_trick([Card(Rank.ACE, Suit.SPADES)])
    card = basic_bot.play( 
        player_index_leading=0,
        trump_suit=Suit.HEARTS,
        cards_played=[],
        taker=1
    )
    assert card == Card(Rank.TEN, Suit.SPADES)


def test_level_one_bot_starts_with_worst_card_if_no_ten_or_ace(basic_bot: BotPlayer):
    card = basic_bot.play( 
        player_index_leading=0,
        trump_suit=Suit.HEARTS,
        cards_played=[],
        taker=1
    )
    assert card == Card(Rank.JACK, Suit.SPADES)


#middle position (2nd or 3rd to play)

def test_level_one_bot_always_play_jack_trump(basic_bot: BotPlayer):
    card = basic_bot.play( 
        player_index_leading=2,
        trump_suit=Suit.SPADES,
        cards_played=[Card(Rank.SEVEN, Suit.SPADES), Card(Rank.QUEEN, Suit.SPADES)],
        taker=3
    )
    assert card == Card(Rank.JACK, Suit.SPADES)


def test_level_one_bot_plays_worst_card_if_trump_led_and_opponent_took(basic_bot: BotPlayer):
    card = basic_bot.play( 
        player_index_leading=1,
        trump_suit=Suit.HEARTS,
        cards_played=[Card(Rank.NINE, Suit.HEARTS)],
        taker=1
    )
    assert card == Card(Rank.QUEEN, Suit.HEARTS)


def test_level_one_bot_cuts_with_best_trump_if_opponent_took(basic_bot: BotPlayer):
    card = basic_bot.play( 
        player_index_leading=1,
        trump_suit=Suit.HEARTS,
        cards_played=[Card(Rank.NINE, Suit.DIAMONDS)],
        taker=1
    )
    assert card == Card(Rank.ACE, Suit.HEARTS)


def test_level_one_bot_cuts_with_best_trump_if_teammate_took(basic_bot: BotPlayer):
    card = basic_bot.play( 
        player_index_leading=1,
        trump_suit=Suit.HEARTS,
        cards_played=[Card(Rank.NINE, Suit.DIAMONDS)],
        taker=2
    )
    assert card == Card(Rank.ACE, Suit.HEARTS)


def test_level_one_bot_keeps_ten_if_ace_not_played(basic_bot: BotPlayer):
    card = basic_bot.play( 
        player_index_leading=1,
        trump_suit=Suit.CLUBS,
        cards_played=[Card(Rank.NINE, Suit.SPADES), Card(Rank.QUEEN, Suit.SPADES)],
        taker=2
    )
    assert card == Card(Rank.JACK, Suit.SPADES)


def test_level_one_bot_plays_ten_if_ace_played(basic_bot: BotPlayer):
    basic_bot.save_trick([Card(Rank.ACE, Suit.SPADES)])
    card = basic_bot.play( 
        player_index_leading=1,
        trump_suit=Suit.CLUBS,
        cards_played=[Card(Rank.NINE, Suit.SPADES), Card(Rank.QUEEN, Suit.SPADES)],
        taker=2
    )
    assert card == Card(Rank.TEN, Suit.SPADES)


#last to play

def test_level_one_bot_wins_trick_if_possible(basic_bot: BotPlayer):
    card = basic_bot.play( 
        player_index_leading=2,
        trump_suit=Suit.CLUBS,
        cards_played=[
            Card(Rank.NINE, Suit.SPADES),
            Card(Rank.QUEEN, Suit.SPADES),
            Card(Rank.ACE, Suit.HEARTS)
        ],
        taker=2
    )
    assert card == Card(Rank.TEN, Suit.SPADES)


def test_level_one_bot_plays_best_card_last_if_teammate_leading(basic_bot: BotPlayer):
    card = basic_bot.play( 
        player_index_leading=2,
        trump_suit=Suit.CLUBS,
        cards_played=[
            Card(Rank.TEN, Suit.DIAMONDS),
            Card(Rank.ACE, Suit.DIAMONDS),
            Card(Rank.SEVEN, Suit.DIAMONDS)
        ],
        taker=2
    )
    assert card == Card(Rank.ACE, Suit.HEARTS)    

def test_level_one_bot_plays_worst_card_if_cant_win_and_opponent_leading(basic_bot: BotPlayer):
    card = basic_bot.play( 
        player_index_leading=1,
        trump_suit=Suit.CLUBS,
        cards_played=[
            Card(Rank.ACE, Suit.SPADES),
            Card(Rank.QUEEN, Suit.SPADES),
            Card(Rank.KING, Suit.SPADES)
        ],
        taker=2
    )
    assert card == Card(Rank.JACK, Suit.SPADES)
#--------------------------------------------------------------------------------
# Static method tests
#--------------------------------------------------------------------------------

def test_player_static_method_one_suit():
    deck = Deck()
    hearts = Player.retrieve_cards_from_container(
        deck._cards,
        suit = Suit.HEARTS
    )
    assert len(hearts) == 8
    assert sum([True if card.suit == Suit.HEARTS else False for card in hearts]) == 8

def test_player_static_method_multiple_suits():
    deck = Deck()
    hearts_spades = Player.retrieve_cards_from_container(
        deck._cards,
        suit = [Suit.HEARTS, Suit.SPADES]
    )
    assert len(hearts_spades) == 16
    assert sum([True if (card.suit == Suit.HEARTS or card.suit == Suit.SPADES)
                else False for card in hearts_spades]) == 16

def test_player_static_method_one_rank():
    deck = Deck()
    aces = Player.retrieve_cards_from_container(
        deck._cards,
        return_type=set,
        rank = Rank.ACE
    )
    assert len(aces) == 4
    assert sum([True if card.rank == Rank.ACE else False for card in aces]) == 4
    assert isinstance(aces, set)

def test_player_static_method_one_suit_one_rank():
    deck = Deck()
    heart_ten = Player.retrieve_cards_from_container(
        deck._cards,
        suit = Suit.HEARTS,
        rank=Rank.TEN
    )
    assert len(heart_ten) == 1
    assert sum([True if card.suit == Suit.HEARTS and card.rank == Rank.TEN
                 else False for card in heart_ten]) == 1