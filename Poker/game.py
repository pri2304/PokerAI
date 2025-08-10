from deck import Deck
from player import Player

class PokerGame:
    def __init__(self, player_names, starting_chips=1000):
        """Initializes list of players, deck which is shuffled, community cards list as empty, dealer position as 0, pot as 0"""
        self.players = [Player(name, starting_chips) for name in player_names]
        self.deck = Deck()
        self.deck.shuffle()
        self.community_cards = []
        self.dealer = 0
        self.pot = 0
        self.pots = []
        self.current_bet = 0
        self.last_raise_size = 0
        self.street = "preflop"
        self.small_blind_amount = 0
        self.big_blind_amount = 0

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
        print(f"Pot: {self.live_pot()}\n")

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

    def live_pot(self):
        return sum(pot["amount"] for pot in getattr(self, "pots", [])) \
            + sum(p.current_bet for p in self.players)

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

        self.current_bet = big_blind
        self.last_raise_size = big_blind

        print(f"{sb_player.name} posts Small Blind: {small_blind}")
        print(f"{bb_player.name} posts Big Blind: {big_blind}")
        print(f"Pot is now {self.live_pot()}")

        self.small_blind_amount = small_blind
        self.big_blind_amount = big_blind
        self.street = "preflop"

    def record_raise(self, target_to):
        old_to = self.current_bet
        delta = max(0, target_to - old_to)

        if target_to > old_to:
            self.current_bet = target_to

        reopened = False
        if delta > 0:
            if self.last_raise_size == 0:
                self.last_raise_size = delta
                reopened = True

            elif delta >= self.last_raise_size:
                self.last_raise_size = delta
                reopened = True

            else:
                reopened = False

        return reopened

    def min_raise(self):
        if self.current_bet == 0:
            return None
        return self.current_bet + self.last_raise_size

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
        """
        One betting street. Uses:
          - self.legal_actions(actor_index)
          - self.record_raise(target_to)
          - self.should_end_betting_round(acted_since_raise)
          - self.collect_bets()  (called at the end to slice pots)
        Default policy for now: CHECK if possible, otherwise CALL (no raises yet).
        """
        num_players = len(self.players)
        actor = starting_player_index
        acted_since_raise = set()

        while True:
            player = self.players[actor]

            # Skip players who can't act
            if player.folded or player.chips == 0:
                # advance turn; check end condition after skipping
                if self.should_end_betting_round(acted_since_raise):
                    break
                actor = (actor + 1) % num_players
                continue

            # What can they legally do?
            actions = self.legal_actions(actor)

            # ---------- YOUR DECISION LOGIC GOES HERE LATER ----------
            # For now: if CHECK is allowed, do it; else CALL.
            # (We won't RAISE yet; you'll wire it where marked below.)
            act = None
            for a in actions:
                if a[0] == "CHECK":
                    act = ("CHECK", 0)
                    break
            if act is None:
                # facing a bet: call (amount is returned by legal_actions)
                call_amt = next((amt for (k, amt, *_) in actions if k == "CALL"), 0)
                act = ("CALL", call_amt)
            # ---------------------------------------------------------

            # Apply the chosen action
            if act[0] == "CHECK":
                # Legal check (your Player.check already handles legality)
                player.check(self.current_bet)
                print(f"{player.name} checks. (Chips Left: {player.chips})")

            elif act[0] == "CALL":
                to_call = max(0, self.current_bet - player.current_bet)
                added = player.call(self.current_bet)  # uses your existing method
                # live pot display = pots already made + current street contributions
                live_pot = self.pot + sum(p.current_bet for p in self.players)
                print(f"{player.name} calls {to_call}, added {added}. Pot: {self.live_pot()}")

            elif act[0] == "RAISE_TO":
                # You’ll use this branch once you start raising.
                target_to = act[1]
                added = player.raise_to(target_to)  # moves chips
                reopened = self.record_raise(target_to)  # updates current_bet / last_raise_size
                live_pot = self.pot + sum(p.current_bet for p in self.players)
                print(f"{player.name} raises to {target_to} (added {added}). Pot: {self.live_pot()}")
                if reopened:
                    acted_since_raise.clear()  # everyone must act again
                # NOTE: remove this whole branch until you're ready to enable raises.

            elif act[0] == "FOLD":
                player.fold()
                print(f"{player.name} folds.")

            # Mark this player as having acted in the current cycle
            acted_since_raise.add(player)

            # Check if the street is done
            if self.should_end_betting_round(acted_since_raise):
                break

            # Next player
            actor = (actor + 1) % num_players

        # End of street: slice contributions into pots and clear per-player current_bet
        self.collect_bets()
        for p in self.players:
            p.current_bet = 0
        print(f"--- End of Betting Round. Pot is now {self.pot} ---\n")

    def collect_bets(self):
        while True:
            nonzero_bets = [p.current_bet for p in self.players if p.current_bet > 0]
            if not nonzero_bets:
                break

            smallest = min(nonzero_bets)
            involved = [p for p in self.players if p.current_bet > 0]

            pot_amount = 0
            for p in involved:
                take = min(p.current_bet, smallest)
                p.current_bet -= take
                pot_amount += take

            eligible = {p for p in involved if not p.folded}
            self.pots.append({"amount": pot_amount, "eligible": eligible})

        self.pot = sum(pot["amount"] for pot in self.pots)

    def players_in_hand(self):
        return [p for p in self.players if not p.folded]

    def players_who_can_act(self):
        return [p for p in self.players if (not p.folded) and (p.chips > 0)]

    def to_call(self, player):
        return max(0, self.current_bet - player.current_bet)

    def everyone_matched_or_all_in(self):
        for p in self.players_in_hand():
            if p.chips > 0 and self.to_call(p) > 0:
                return False
            return True

    def should_end_betting_round(self, acted_since_raise: set):
        remaining = self.players_in_hand()
        if len(remaining) <= 1:
            return True

        if not self.everyone_matched_or_all_in():
            return False

        need_to_have_acted = set(self.players_who_can_act())
        return need_to_have_acted.issubset(acted_since_raise)

    def is_heads_up(self):
        """Treat it as heads-up if 2 or fewer players are still in the hand."""
        active = [p for p in self.players if not p.folded]
        return len(active) <= 2

    def first_to_act_preflop(self):
        """
        Multi-way: UTG (seat after BB).
        Heads-up: SB acts first preflop (SB is dealer in HU).
        """
        n = len(self.players)
        if self.is_heads_up():
            return self.small_blind_pos  # SB acts first HU preflop
        return (self.big_blind_pos + 1) % n  # UTG

    def first_to_act_postflop(self):
        """Postflop, first to act is always seat after dealer."""
        n = len(self.players)
        return (self.dealer + 1) % n

    def bb_can_check_now(self, actor_index):
        """
        Preflop only. True if actor is the BB and there was no raise above the blind:
        i.e., to_call == 0 and current_bet == big_blind_amount.
        """
        if self.street != "preflop":
            return False
        if actor_index != self.big_blind_pos:
            return False
        player = self.players[actor_index]
        to_call = max(0, self.current_bet - player.current_bet)
        # No raise above BB happened if current_bet equals the blind amount.
        return to_call == 0 and self.current_bet == self.big_blind_amount

    def legal_actions(self, actor_index: int):
        """
        Return the list of legal actions for the player at seat `actor_index`.
        Format: [("CHECK", 0),
                 ("CALL", amount),
                 ("FOLD", 0),
                 ("RAISE_TO", target_to, {"reopens": bool}), ...]
        """
        p = self.players[actor_index]

        # If they’re out of the hand or out of chips, nothing to do
        if p.folded or p.chips == 0:
            return []

        actions = []

        # How much they need to match the table to-level
        to_call = max(0, self.current_bet - p.current_bet)

        # 1) Check / Call / Fold
        if to_call == 0:
            actions.append(("CHECK", 0))
            # (We usually don't offer FOLD when you can check.)
        else:
            actions.append(("CALL", min(to_call, p.chips)))
            actions.append(("FOLD", 0))

        # 2) Raise options
        max_to = p.current_bet + p.chips  # all-in to-level ceiling

        # Compute minimum legal raise *to-level*
        if self.current_bet == 0:
            # Opening bet on this street: use BB as the table minimum
            min_target = getattr(self, "big_blind_amount", 0)
        else:
            base = self.last_raise_size if self.last_raise_size > 0 else getattr(self, "big_blind_amount", 0)
            min_target = self.current_bet + base

        # Can the player go above the current to-level at all?
        if max_to > self.current_bet:
            # Case A: they can’t reach the min raise → short all-in (does NOT reopen)
            if max_to < min_target:
                actions.append(("RAISE_TO", max_to, {"reopens": False}))
            else:
                # Case B: at least a full raise is possible (does reopen)
                actions.append(("RAISE_TO", min_target, {"reopens": True}))
                if max_to > min_target:
                    # Also expose shove option
                    actions.append(("RAISE_TO", max_to, {"reopens": True}))

        return actions

    def showdown(self):
        """checks who won, then declares result"""

        contenders = [p for p in self.players if not p.folded]
        for p in contenders:
            p.evaluate_best_hand(self.community_cards)

        ranked = sorted(contenders, key=lambda pl: (pl.best_hand[0], pl.best_hand[1]), reverse=True)
        print("\n--- SHOWDOWN ---")
        for pl in ranked:
            print(f"  {pl.name:7}: {pl.pretty_hand()}")

        if any(p.current_bet > 0 for p in self.players):
            self.collect_bets()

        for i, pot in enumerate(self.pots, start=1):
            elig = [p for p in contenders if p in pot["eligible"]]
            if not elig or pot["amount"] == 0:
                continue

            best_key = max((p.best_hand[0], p.best_hand[1]) for p in elig)
            winners = [p for p in elig if (p.best_hand[0], p.best_hand[1]) == best_key]

            share = pot["amount"] // len(winners)
            remainder = pot["amount"] % len(winners)

            for w in winners:
                w.chips += share

            if remainder:
                order = [(idx % len(self.players)) for idx in range(self.dealer + 1, self.dealer + 1 + len(self.players))]
                winners_by_seat = sorted(winners, key = lambda w: order.index(self.players.index(w)))
                for j in range(remainder):
                    winners_by_seat[j % len(winners_by_seat)].chips += 1

            print(f"Pot (i): {pot['amount']} → {', '.join(w.name for w in winners)}" f" (+{share}{' + remainder distributed' if remainder else ''})")
        self.pots = []
        self.pot = 0
