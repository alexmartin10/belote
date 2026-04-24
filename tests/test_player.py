from backend.game.player import BotPlayer, AlwaysTakingBot
from backend.game.card import Card, Rank, Suit
import pytest

def same_elements(a, b):
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
    player = BotPlayer(0, 'bot')
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
    player = AlwaysTakingBot(1, 'taker')
    player.set_player_index(0)
    player.make_hand([
        Card(Rank.TEN, Suit.SPADES),
        Card(Rank.JACK, Suit.SPADES),
        Card(Rank.ACE, Suit.HEARTS),
        Card(Rank.QUEEN, Suit.HEARTS),
    ])
    return player

def test_basicbot_playable_cards_first_card_is_better_trump(basic_bot: BotPlayer):
    """cas ou on commence à l'atout, un atout meilleur que les notres"""
    trump_suit = Suit.HEARTS
    cards_played = [
        Card(Rank.JACK, Suit.HEARTS),
        Card(Rank.SEVEN, Suit.DIAMONDS)
    ]

    assert same_elements(
        basic_bot.playable_cards(cards_played, trump_suit),
        [Card(Rank.QUEEN, Suit.HEARTS), Card(Rank.ACE, Suit.HEARTS)]
    ) == True

def test_basicbot_playable_cards_first_card_is_lower_trump(basic_bot: BotPlayer):
    """cas ou on commence à l'atout, un atout moins bon que les notres"""
    trump_suit = Suit.HEARTS
    cards_played = [Card(Rank.EIGHT, Suit.HEARTS)]

    assert same_elements(
        basic_bot.playable_cards(cards_played, trump_suit),
        [Card(Rank.QUEEN, Suit.HEARTS), Card(Rank.ACE, Suit.HEARTS)]
    ) == True

def test_basicbot_playable_cards_first_card_is_between_trump(basic_bot: BotPlayer):
    """cas ou on commence à l'atout, un atout entre les notres"""
    trump_suit = Suit.HEARTS
    cards_played = [Card(Rank.TEN, Suit.HEARTS)]

    assert basic_bot.playable_cards(cards_played, trump_suit) == [Card(Rank.ACE, Suit.HEARTS)]
    
def test_basicbot_playable_cards_cut(basic_bot: BotPlayer):
    """cas ou on coupe"""
    trump_suit = Suit.HEARTS
    cards_played = [Card(Rank.JACK, Suit.CLUBS)]

    assert same_elements(
        basic_bot.playable_cards(cards_played, trump_suit),
        [Card(Rank.QUEEN, Suit.HEARTS), Card(Rank.ACE, Suit.HEARTS)]
    ) == True

def test_basicbot_playable_cards_cut_higher(basic_bot: BotPlayer):
    """cas ou on doit monter en coupant"""
    trump_suit = Suit.HEARTS
    cards_played = [
        Card(Rank.JACK, Suit.CLUBS),
        Card(Rank.EIGHT, Suit.HEARTS)
    ]

    assert same_elements(
        basic_bot.playable_cards(cards_played, trump_suit),
        [Card(Rank.QUEEN, Suit.HEARTS), Card(Rank.ACE, Suit.HEARTS)]
    ) == True

def test_basicbot_playable_cards_cut_lower(basic_bot: BotPlayer):
    """cas ou on ne peut pas monter en coupant"""
    trump_suit = Suit.HEARTS
    cards_played = [
        Card(Rank.JACK, Suit.CLUBS),
        Card(Rank.NINE, Suit.HEARTS)
    ]

    assert same_elements(
        basic_bot.playable_cards(cards_played, trump_suit),
        [Card(Rank.QUEEN, Suit.HEARTS), Card(Rank.ACE, Suit.HEARTS)]
    ) == True

def test_basicbot_first_player(basic_bot: BotPlayer):
    """cas ou on commence la partie"""
    trump_suit = Suit.HEARTS
    cards_played = []
    assert same_elements(
        basic_bot.playable_cards(cards_played, trump_suit),
        basic_bot.hand
    )

def test_basicbot_playable_cards_no_better_trump_in_hand(basic_bot: BotPlayer):
    """cas ou on ne peut pas monter en coupant"""
    trump_suit = Suit.HEARTS
    cards_played = [
        Card(Rank.JACK, Suit.HEARTS),
        Card(Rank.NINE, Suit.HEARTS)
    ]

    assert same_elements(
        basic_bot.playable_cards(cards_played, trump_suit),
        [Card(Rank.ACE, Suit.HEARTS),Card(Rank.QUEEN, Suit.HEARTS)]
    ) == True

def test_basicbot_playable_cards_no_trump_in_hand(basic_bot: BotPlayer):
    """cas ou on n'a pas d'atout"""
    trump_suit = Suit.CLUBS
    cards_played = [
        Card(Rank.JACK, Suit.CLUBS),
        Card(Rank.NINE, Suit.CLUBS)
    ]

    assert same_elements(
        basic_bot.playable_cards(cards_played, trump_suit),
        basic_bot.hand
    ) == True

def test_basicbot_playable_cards_cant_cut(basic_bot: BotPlayer):
    """cas ou on n'a pas d'atout pour couper"""
    trump_suit = Suit.DIAMONDS
    cards_played = [
        Card(Rank.JACK, Suit.CLUBS),
        Card(Rank.NINE, Suit.CLUBS)
    ]

    assert same_elements(
        basic_bot.playable_cards(cards_played, trump_suit),
        basic_bot.hand
    ) == True

def test_bot_plays_strongest_when_leading(basic_bot: BotPlayer):
    """quand l'équipe mène, le bot joue la carte la plus forte"""
    trump_suit = Suit.HEARTS
    cards_played = [
        Card(Rank.ACE, Suit.SPADES),
        Card(Rank.QUEEN, Suit.SPADES)
    ]
    # player 0, leading player 2 → même équipe (0+2 vs 1+3)
    card = basic_bot.play(
        player_index_leading=2,
        trump_suit=trump_suit,
        cards_played=cards_played
    )
    assert card == Card(Rank.TEN, Suit.SPADES)

def test_bot_plays_weakest_when_not_leading(basic_bot: BotPlayer):
    """quand l'équipe ne mène pas, le bot joue la carte la plus faible"""
    trump_suit = Suit.HEARTS
    cards_played = [
        Card(Rank.ACE, Suit.SPADES),
        Card(Rank.QUEEN, Suit.SPADES),
        Card(Rank.SEVEN, Suit.SPADES)
    ]
    # player 0, leading player 1 → équipe adverse
    card = basic_bot.play(
        player_index_leading=1,
        trump_suit=trump_suit,
        cards_played=cards_played
    )
    assert card == Card(Rank.JACK, Suit.SPADES)

def test_bot_card_removed_from_hand(basic_bot: BotPlayer):
    """la carte jouée doit être retirée de la main"""
    trump_suit = Suit.HEARTS
    cards_played = []
    hand_size_before = len(basic_bot.hand)
    card = basic_bot.play(
        player_index_leading=2,
        trump_suit=trump_suit,
        cards_played=cards_played
    )
    basic_bot.remove_card_played(card)
    assert len(basic_bot.hand) == hand_size_before - 1
    assert card not in basic_bot.hand


#TAKER BOT
def test_takerbot_playable_cards_first_card_is_better_trump(taker_bot: AlwaysTakingBot):
    """cas ou on commence à l'atout, un atout meilleur que les notres"""
    trump_suit = Suit.HEARTS
    cards_played = [
        Card(Rank.JACK, Suit.HEARTS),
        Card(Rank.SEVEN, Suit.DIAMONDS)
    ]

    assert same_elements(
        taker_bot.playable_cards(cards_played, trump_suit),
        [Card(Rank.QUEEN, Suit.HEARTS), Card(Rank.ACE, Suit.HEARTS)]
    ) == True

def test_takerbot_playable_cards_first_card_is_lower_trump(taker_bot: AlwaysTakingBot):
    """cas ou on commence à l'atout, un atout moins bon que les notres"""
    trump_suit = Suit.HEARTS
    cards_played = [Card(Rank.EIGHT, Suit.HEARTS)]

    assert same_elements(
        taker_bot.playable_cards(cards_played, trump_suit),
        [Card(Rank.QUEEN, Suit.HEARTS), Card(Rank.ACE, Suit.HEARTS)]
    ) == True

def test_takerbot_playable_cards_first_card_is_lower_trump(taker_bot: AlwaysTakingBot):
    """cas ou on commence à l'atout, un atout entre les notres"""
    trump_suit = Suit.HEARTS
    cards_played = [Card(Rank.TEN, Suit.HEARTS)]

    assert taker_bot.playable_cards(cards_played, trump_suit) == [Card(Rank.ACE, Suit.HEARTS)]
    
def test_takerbot_playable_cards_cut(taker_bot: AlwaysTakingBot):
    """cas ou on coupe"""
    trump_suit = Suit.HEARTS
    cards_played = [Card(Rank.JACK, Suit.CLUBS)]

    assert same_elements(
        taker_bot.playable_cards(cards_played, trump_suit),
        [Card(Rank.QUEEN, Suit.HEARTS), Card(Rank.ACE, Suit.HEARTS)]
    ) == True

def test_takerbot_playable_cards_cut_higher(taker_bot: AlwaysTakingBot):
    """cas ou on doit monter en coupant"""
    trump_suit = Suit.HEARTS
    cards_played = [
        Card(Rank.JACK, Suit.CLUBS),
        Card(Rank.EIGHT, Suit.HEARTS)
    ]

    assert same_elements(
        taker_bot.playable_cards(cards_played, trump_suit),
        [Card(Rank.QUEEN, Suit.HEARTS), Card(Rank.ACE, Suit.HEARTS)]
    ) == True

def test_takerbot_playable_cards_cut_lower(taker_bot: AlwaysTakingBot):
    """cas ou on ne peut pas monter en coupant"""
    trump_suit = Suit.HEARTS
    cards_played = [
        Card(Rank.JACK, Suit.CLUBS),
        Card(Rank.NINE, Suit.HEARTS)
    ]

    assert same_elements(
        taker_bot.playable_cards(cards_played, trump_suit),
        [Card(Rank.QUEEN, Suit.HEARTS), Card(Rank.ACE, Suit.HEARTS)]
    ) == True

def test_takerbot_first_player(taker_bot: AlwaysTakingBot):
    """cas ou on commence la partie"""
    trump_suit = Suit.HEARTS
    cards_played = []
    assert same_elements(
        taker_bot.playable_cards(cards_played, trump_suit),
        taker_bot.hand
    )

def test_takerbot_playable_cards_no_trump_in_hand(taker_bot: AlwaysTakingBot):
    """cas ou on ne peut pas monter en coupant"""
    trump_suit = Suit.CLUBS
    cards_played = [
        Card(Rank.JACK, Suit.CLUBS),
        Card(Rank.NINE, Suit.CLUBS)
    ]

    assert same_elements(
        taker_bot.playable_cards(cards_played, trump_suit),
        taker_bot.hand
    ) == True

def test_takerbot_playable_cards_no_trump_in_hand(taker_bot: AlwaysTakingBot):
    """cas ou on n'a pas d'atout"""
    trump_suit = Suit.CLUBS
    cards_played = [
        Card(Rank.JACK, Suit.CLUBS),
        Card(Rank.NINE, Suit.CLUBS)
    ]

    assert same_elements(
        taker_bot.playable_cards(cards_played, trump_suit),
        taker_bot.hand
    ) == True

def test_takerbot_playable_cards_cant_cut(taker_bot: AlwaysTakingBot):
    """cas ou on n'a pas d'atout pour couper"""
    trump_suit = Suit.DIAMONDS
    cards_played = [
        Card(Rank.JACK, Suit.CLUBS),
        Card(Rank.NINE, Suit.CLUBS)
    ]

    assert same_elements(
        taker_bot.playable_cards(cards_played, trump_suit),
        taker_bot.hand
    ) == True