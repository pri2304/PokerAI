from hand_evaluator import evaluate_hand, format_hand_result


class Player:
    def __init__(self, name, chips=1000):
        self.name = name
        self.chips = chips
        self.hole_cards = []
        self.folded = False
        self.current_bet = 0
        self.best_hand = None

    def receive_cards(self, cards):
        """Give the player cards"""

        self.hole_cards.extend(cards)

    def fold(self):
        """Mark player as folded."""
        self.folded = True

    def reset_hand(self):
        """Clear hole cards and reset status for a new round."""
        self.hole_cards = []
        self.folded = False
        self.current_bet = 0
        self.best_hand = None

    def bet(self, amount):
        """helps calculate the bet amount and remaining chips amount"""
        if amount >= self.chips:
            amount = self.chips
            self.chips = 0
        else:
            self.chips -= amount

        self.current_bet += amount
        return amount


    def call(self, highest_bet):
        """Calculates Call amount and chips after calling"""
        amount_to_call = highest_bet - self.current_bet

        if amount_to_call >= self.chips:
            amount_to_call = self.chips
            self.chips = 0
        else:
            self.chips -= amount_to_call

        self.current_bet += amount_to_call
        return amount_to_call

    def check(self, highest_bet):
        """Checks if /"check"/ condition is possible"""
        if highest_bet == 0:
            return True
        else:
            return False

    def __str__(self):
        cards_str = ' ,'.join(str(card) for card in self.hole_cards)
        return f"{self.name}: {cards_str} (Chips : {self.chips})"

    def evaluate_best_hand(self, board_cards):
        self.best_hand = evaluate_hand(self.hole_cards + board_cards)

    def pretty_hand(self):
        rv, tie, five = self.best_hand
        five_str = ' '.join(str(c) for c in five)
        return f"{format_hand_result(rv, tie):45} | {five_str}"


