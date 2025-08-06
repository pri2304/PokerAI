from deck import Deck
from player import Player
from hand_evaluator import format_hand_result

class PokerGame:
    def __init__(self, player_names, starting_chips=1000):
        """Initializes list of players, deck which is shuffled, community cards list as empty, dealer position as 0, pot as 0"""
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
        """Creates a readable log for rounds"""
        print("\n--- Current Table ---")
        print(f"Pot: {self.pot}\n")

        dealer_pos = self.dealer #gets position for dealer
        sb_pos = getattr(self, "small_blind_pos", None) #gets position for small blind player
        bb_pos = getattr(self, "big_blind_pos", None) #gets position for big blind player

        for idx, player in enumerate(self.players): #used to track not only player but position in table as well
            status = "FOLDED" if player.folded else "ACTIVE"
            role = []
            if idx == dealer_pos:
                role.append("D")
            if idx == sb_pos:
                role.append("SB")
            if idx == bb_pos:
                role.append("BB")
            role_str = ",".join(role) if role else "-"

            cards = ', '.join(str(card) for card in player.hole_cards) if player.hole_cards else "(no cards)"
            print(f"{player.name:6} | {status:6} | Chips: {player.chips:4} | Role: {role_str:4} | Cards: {cards}")

        community = ', '.join(str(card) for card in self.community_cards) if self.community_cards else "(none)"
        print(f"\nCommunity Cards: {community}")
        print("---------------------------\n")

    def post_blinds(self, small_blind, big_blind):
        """adds the big blind and small blind from respective players to the pot"""
        num_players = len(self.players)
        self.small_blind_pos = (self.dealer + 1) % num_players
        self.big_blind_pos = (self.dealer + 2) % num_players
        """tracks sb and bb positions"""

        sb_player = self.players[self.small_blind_pos]
        bb_player = self.players[self.big_blind_pos]

        sb_amount = sb_player.bet(small_blind)
        bb_amount = bb_player.bet(big_blind)

        self.pot = big_blind + small_blind #adds the big blind and small blind to pot

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
            player.best_hand = None

    def start_round(self, small_blind, big_blind):
        """resets hand + rotates the blinds + posts blinds for new round"""
        self.start_new_hand()
        self.post_blinds(small_blind, big_blind)

    def betting_round(self, starting_player_index):
        """maintains the betting loop for the round"""
        num_player = len(self.players)
        current_bet = max(p.current_bet for p in self.players)
        active_players = [p for p in self.players if not p.folded and p.chips > 0]

        player_index = starting_player_index
        acted_players = set() #players who already took an action

        while True: #betting loop
            player = self.players[player_index]

            if player.folded or player.chips == 0:
                player_index = (player_index + 1) % num_player
                continue #goes to next player

            acted_players.add(player)

            if current_bet == 0: #checks
                player.check(current_bet)
                print(f"{player.name} checks. (Chips Left: {player.chips})")

            else:
                if player.chips + player.current_bet >= current_bet: #calls
                    amount = player.call(current_bet)
                    self.pot += amount
                    print(f"{player.name} calls to {current_bet}, added {amount}. Pot: {self.pot}")

                else: #folds
                    player.fold()
                    print(f"{player.name} folded")

            remaining = [p for p in active_players if not p.folded]
            all_matched = all(p.folded or p.current_bet == current_bet for p in active_players) #checks if all active players have matched

            if (all_matched and acted_players.issuperset(remaining)) or len(remaining) == 1: #condition to check if round is over
                break

            player_index = (player_index + 1) % num_player

        for p in self.players: #resets current bet for all players for next round
            p.current_bet = 0

        print(f"--- End of Betting Round. Pot is now {self.pot} ---\n")

    def showdown(self):
        """checks who won, then declares result"""

        for p in self.players:
            if not p.folded:
                p.evaluate_best_hand(self.community_cards) #checks best hand for each player

        ranked = sorted([p for p in self.players if not p.folded], key=lambda pl: (pl.best_hand[0], pl.best_hand[1]), reverse=True) #ranks all player's best hands in order to determine winner

        top_rank, top_tie = ranked[0].best_hand[:2] #winner's rank and tiebreaker
        winners = [pl for pl in ranked if (pl.best_hand[0], pl.best_hand[1]) == (top_rank, top_tie)] #checks for all winners and adds them to list

        print("\n--- SHOWDOWN ---")
        for pl in ranked:
            mark = "🏆" if pl in winners else " " #prints all winner names
            print(f"{mark} {pl.name:7}: {pl.pretty_hand()}")

        share = self.pot // len(winners) #splits pot between winners
        for w in winners:
            w.chips += share
        print(f"\nWinners: {', '.join(w.name for w in winners)} "
              f"collect {share} chips each\n")

        self.pot = 0


