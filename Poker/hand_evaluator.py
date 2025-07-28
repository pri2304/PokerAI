from deck import Card

def evaluate_hand(cards):
    """
    Evaluate the best 5-card poker hand from 7 cards.
    Returns a tuple: (rank_value, tiebreakers)
    rank_value: 0 (High Card) to 8 (Straight Flush)
    tiebreakers: list of card ranks in descending order for tie-breaking
    """
    # Step 1: Prepare counts
    rank_counts = get_rank_counts(cards)
    suit_counts = get_suit_counts(cards)

    # Step 2: Check each hand type in order (highest first)
    result = check_straight_flush(cards, suit_counts)
    if result: return (8, result)

    result = check_four_of_a_kind(rank_counts, cards)
    if result: return (7, result)

    result = check_full_house(rank_counts)
    if result: return (6, result)

    result = check_flush(suit_counts)
    if result: return (5, result)

    result = check_straight(cards)
    if result: return (4, result)

    result = check_three_of_a_kind(rank_counts, cards)
    if result: return (3, result)

    result = check_two_pair(rank_counts, cards)
    if result: return (2, result)

    result = check_one_pair(rank_counts, cards)
    if result: return (1, result)

    # High card fallback
    return (0, get_high_cards(cards))

def get_rank_counts(cards):
    """Return a dict: {rank_value: count} for all cards."""
    rank_counts = {}
    for card in cards:
        rank_counts[card.value] = rank_counts.get(card.value, 0) + 1
    return rank_counts

def get_suit_counts(cards):
    """Return a dict: {suit: [rank_values]} for all cards."""
    suit_counts = {}
    for card in cards:
        suit_counts.setdefault(card.suit, []).append(card.value)
    return suit_counts

def check_straight_flush(cards, suit_counts):
    """Return top 5 ranks for a straight flush, or None."""
    for suit, ranks in suit_counts.items():
        if len(ranks) < 5:
            continue

        ranks = sorted(set(ranks), reverse=True)

        if 14 in ranks:
            ranks.append(1)

        for i in range(len(ranks) - 4):
            window = ranks[i:i + 5]

            if max(window) - min(window) == 4 and len(set(window))==5:
                return sorted(window, reverse=True)

    return None

def check_four_of_a_kind(rank_counts, cards):
    """Return [quad_rank, kicker] or None."""
    quad_rank = None
    for rank, count in rank_counts.items():
        if count == 4:
            quad_rank = rank
            break

        if not quad_rank:
            return None

    kicker_ranks = [card.value for card in cards if card.value != quad_rank]
    kicker = max(kicker_ranks) if kicker_ranks else None

    return [quad_rank, kicker]

def check_full_house(rank_counts):
    """Return [triple_rank, pair_rank] or None."""
    triples = [rank for rank, count in rank_counts.items() if count >= 3]
    pairs = [rank for rank, count in rank_counts.items() if count >= 2]

    if not triples:
        return None

    triples.sort(reverse=True)
    pairs.sort(reverse=True)

    triple_rank = triples[0]

    pair_rank = None
    for rank in pairs:
        if rank != triple_rank:
            pair_rank = rank
            break

    if not pair_rank and len(triples) >1:
        pair_rank = triples[1]

    if triple_rank and pair_rank:
        return [triple_rank, pair_rank]

    return None


def check_flush(suit_counts):
    """Return top 5 ranks of flush, or None."""

    best_flush = None

    for suit, ranks in suit_counts.items():
        if len(ranks) >= 5:

            top5 = sorted(ranks, reverse=True)[:5]

            if not best_flush or top5 > best_flush:
                best_flush = top5

    return best_flush

def check_straight(cards):
    """Return top 5 ranks of straight, or None (Ace high or low)."""
    ranks = sorted({card.value for card in cards}, reverse=True)

    if 14 in ranks:
        ranks.append(1)

    for i in range(len(ranks) - 4):
        window = ranks[i:i + 5]

        if max(window) - min(window) == 4 and len(set(window))==5:
            return sorted(window, reverse=True)

    return None

def check_three_of_a_kind(rank_counts, cards):
    """Return [triple_rank, kicker1, kicker2] or None."""
    triples = [rank for rank, count in rank_counts.items() if count == 3]

    if not triples:
        return None

    triples.sort(reverse=True)
    triple_rank = triples[0]

    kickers = [card.value for card in cards if card.value != triple_rank]
    kickers = sorted(set(kickers), reverse=True)[:2]

    return [triple_rank] + kickers


def check_two_pair(rank_counts, cards):
    """Return [high_pair, low_pair, kicker] or None."""
    pairs = [rank for rank, count in rank_counts.items() if count >= 2]

    if len(pairs) < 2:
        return None

    pairs.sort(reverse=True)
    high_pair, low_pair = pairs[:2]

    kickers = [card.value for card in cards if card.value not in (high_pair, low_pair)]
    kicker = max(kickers) if kickers else None

    return [high_pair, low_pair, kicker]

def check_one_pair(rank_counts, cards):
    """Return [pair_rank, kicker1, kicker2, kicker3] or None."""
    pairs = [rank for rank, count in rank_counts.items() if count >= 2]

    if not pairs:
        return None

    pairs.sort(reverse=True)
    pair_rank=pairs[0]

    kickers = [card.value for card in cards if card.value != pair_rank]
    kickers = sorted(set(kickers), reverse=True)[:3]

    return [pair_rank] + kickers

def get_high_cards(cards):
    """Return top 5 ranks (for High Card case or Kickers)."""
    ranks = sorted({card.value for card in cards}, reverse=True)
    return ranks[:5]

def format_hand_result(rank_value, tiebreakers):
    """Turn a hand evaluation result into a readable string."""
    RANK_NAMES = {2:"Two", 3:"Three", 4:"Four", 5:"Five", 6:"Six", 7:"Seven", 8:"Eight", 9:"Nine", 10:"Ten", 11:"Jack", 12:"Queen", 13:"King", 14:"Ace"}
    def name_card(value):
        return RANK_NAMES.get(value, str(value))

    if rank_value == 8:
        if tiebreakers[0] == 14 and tiebreakers[1] == 13:
            return "Royale Flush"
        return f"Straight Flush, {name_card(tiebreakers[0])}-high"

    if rank_value == 7:
        return f"Four of a Kind, {name_card(tiebreakers[0])}s with {name_card(tiebreakers[1])} kicker"

    if rank_value == 6:
        return f"Full House, {name_card(tiebreakers[0])}s over {name_card(tiebreakers[1])}s"

    if rank_value == 5:
        cards = ', '.join(name_card(v) for v in tiebreakers)
        return f"Flush, high cards {cards}"

    if rank_value == 4:
        return f"Straight, {name_card(tiebreakers[0])}-high"

    if rank_value == 3:
        kickers = ', '.join(name_card(v) for v in tiebreakers[1:])
        return f"Three of a Kind, {name_card(tiebreakers[0])}s with kickers {kickers}"

    if rank_value == 2:
        kicker = name_card(tiebreakers[2])
        return f"Two Pair, {name_card(tiebreakers[0])}s and {name_card(tiebreakers[1])}s with kicker {kicker}"

    if rank_value == 1:
        kickers = ', '.join(name_card(v) for v in tiebreakers[1:])
        return f"One Pair, {name_card(tiebreakers[0])}s with kickers {kickers}"

    if rank_value == 0:
        cards = ', '.join(name_card(v) for v in tiebreakers)
        return f"High Card, {cards}"

    return None
