import random

class Card:
    '''Maps the ranks to actual numeric values'''
    Rank_Values = {
        '2': 2,
        '3': 3,
        '4': 4,
        '5': 5,
        '6': 6,
        '7': 7,
        '8': 8,
        '9': 9,
        '10': 10,
        'J': 11,
        'Q': 12,
        'K': 13,
        'A': 14
        }
    def __init__(self, rank, suit):
        self.suit = suit
        self.rank = rank
        self.value = self.Rank_Values[rank] #actual numeric value of card

    def __str__(self):
        return f"{self.rank}{self.suit}" #to print card

    def alt_value(self):
        """Return 1 for Ace (used in A-2-3-4-5 straights)."""
        return 1 if self.rank == 'A' else self.value


class Deck:
    def __init__(self):
        self.cards = []
        self.build_deck() #calls build_deck

    def build_deck(self):
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        suits = ['♠', '♥', '♦', '♣']
        self.cards = [Card(rank, suit) for rank in ranks for suit in suits] #builds a deck with all 52 cards

    def __str__(self):
        return ', '.join(str(Card) for Card in self.cards) #to print deck

    def shuffle(self):
        random.shuffle(self.cards) #shuffle's cards

    def deal(self, num=1):
        """Deal `num` cards and remove them from the deck."""
        if num > len(self.cards):
            raise ValueError("Not enough cards in the deck!")
        dealt = self.cards[:num]
        self.cards = self.cards[num:]
        return dealt

    def __repr__(self):
        return self.__str__()

