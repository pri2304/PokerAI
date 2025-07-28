from deck import Deck
from player import Player

class PokerGame:
    def __init__(self, player_names, starting_chips=1000):
        self.players = [Player(name, starting_chips) for name in player_names]
        self.deck = Deck()
        self.deck.shuffle()
        self.community_cards = []
        self.dealer = 0
        self.pot = 0

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

    def post_blinds(self, small_blind, big_blind):
        """adds the big blind and small blind from respective players to the pot"""
        num_players = len(self.players)
        self.small_blind_pos = (self.dealer + 1) % num_players
        self.big_blind_pos = (self.dealer + 2) % num_players

        sb_player = self.players[self.small_blind_pos]
        bb_player = self.players[self.big_blind_pos]

        sb_amount = sb_player.bet(small_blind)
        bb_amount = bb_player.bet(big_blind)

        self.pot = big_blind + small_blind

        print(f"{sb_player.name} posts Small Blind: {small_blind}")
        print(f"{bb_player.name} posts Big Blind: {big_blind}")
        print(f"Pot is now {self.pot}")

    def start_new_hand(self):
        """resets everything for a new round"""
        self.dealer = (self.dealer + 1) % len(self.players)

        self.pot = 0
        self.community_cards = []

        self.deck = Deck()
        self.deck.shuffle()

        for player in self.players:
            player.hole_cards = []
            player.current_bet = 0
            player.folded = False

    def start_round(self, small_blind, big_blind):
        """resets hand + rotates the blinds"""
        self.start_new_hand()
        self.post_blinds(small_blind, big_blind)


