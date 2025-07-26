class Player:
    def __init__(self, name, chips=1000):
        self.name = name
        self.chips = chips
        self.hole_cards = []
        self.folded = False

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

    def __str__(self):
        cards_str = ' ,'.join(str(card) for card in self.hole_cards)
        return f"{self.name}: {cards_str} (Chips : {self.chips})"


