from deck import Deck
from player import Player

class PokerGame:
    def __init__(self, player_names, starting_chips=1000):
        self.players = [Player(name, starting_chips) for name in player_names]
        self.deck = Deck()
        self.deck.shuffle()
        self.community_cards = []

    def deal_initial_hands(self):
        """Deal 2 hole cards to each player."""
        for player in self.players:
            player.receive_cards(self.deck.deal(2))

    def deal_flop(self):
        """Burn 1 Card, then Deal first 3 community cards"""
        self.deck.deal(1)
        self.community_cards.extend(self.deck.deal(3))

    def deal_turn(self):
        """Burn 1 Card, then Deal 1 more community card"""
        self.deck.deal(1)
        self.community_cards.extend(self.deck.deal(1))

    def deal_river(self):
        """Burn 1 Card, then Deal 1 last community card"""
        self.deck.deal(1)
        self.community_cards.extend(self.deck.deal(1))

    def show_table(self):
        print("\n---Current Table---")
        for player in self.players:
            print(player)
        print("Community Cards", ', '.join(str(card) for card in self.community_cards))
        print("---------------------\n")
