def evaluate_hand(cards):
    """
    Evaluate the best 5-card poker hand from 7 cards.
    Returns a tuple: (rank_value, tiebreakers, best hand_cards)
    rank_value: 0 (High Card) to 8 (Straight Flush)
    tiebreakers: list of card ranks in descending order for tie-breaking
    hand_cards: the actual 5 best card hand
    """
    # Step 1: Prepare counts
    rank_counts = get_rank_counts(cards)
    suit_counts = get_suit_counts(cards)

    # Step 2: Check each hand type in order (highest first)
    result = check_straight_flush(cards, suit_counts)
    if result:
        tiebreakers, hand_cards = result
        return (8, tiebreakers, hand_cards)

    result = check_four_of_a_kind(rank_counts, cards)
    if result:
        tiebreakers, hand_cards = result
        return (7, tiebreakers, hand_cards)

    result = check_full_house(rank_counts, cards)
    if result:
        tiebreakers, hand_cards = result
        return (6, tiebreakers, hand_cards)

    result = check_flush(suit_counts, cards)
    if result:
        tiebreakers, hand_cards = result
        return (5, tiebreakers, hand_cards)

    result = check_straight(cards)
    if result:
        tiebreakers, hand_cards = result
        return (4, tiebreakers, hand_cards)

    result = check_three_of_a_kind(rank_counts, cards)
    if result:
        tiebreakers, hand_cards = result
        return (3, tiebreakers, hand_cards)

    result = check_two_pair(rank_counts, cards)
    if result:
        tiebreakers, hand_cards = result
        return (2, tiebreakers, hand_cards)

    result = check_one_pair(rank_counts, cards)
    if result:
        tiebreakers, hand_cards = result
        return (1, tiebreakers, hand_cards)

    top5 = sorted(cards, key=lambda c: c.value, reverse=True)[:5] #defaults to high card
    return (0, [c.value for c in top5], top5)

def get_rank_counts(cards):
    """Return a dict: {rank_value: count} for all cards."""
    rank_counts = {}
    for card in cards:
        rank_counts[card.value] = rank_counts.get(card.value, 0) + 1 #adds a count for a rank value present
    return rank_counts

def get_suit_counts(cards):
    """Return a dict: {suit: [rank_values]} for all cards."""
    suit_counts = {}
    for card in cards:
        suit_counts.setdefault(card.suit, []).append(card.value) #adds a rank value to respective suit's list
    return suit_counts

def check_straight_flush(cards, suit_counts):
    """Return top 5 ranks for a straight flush, or None. Also returns the cards"""
    for suit in suit_counts: #loops through all suits
        suited = [c for c in cards if c.suit == suit] #checks if suited is less than 5, if yes it will check next suit
        if len(suited) < 5:
            continue

        suited.sort(key=lambda c: c.value, reverse=True) #sorts list in order by rank values

        uniq = sorted({c.value for c in suited}, reverse = True) #converts list to set to remove duplicates
        if 14 in uniq: #condition if Ace exists in suited
            uniq.append(1)

        for i in range(len(uniq) -4): #loops through all possible straights
            run = uniq[i:i+5]
            if run[0] - run[4] == 4 and len(set(run)) == 5: #condition to check for straight
                needed = set(run)
                hand = []
                for c in suited: #if straight it will then convert the set into a list of cards
                    if c.value in needed:
                        hand.append(c)
                        needed.remove(c.value)
                    if len(hand) == 5:
                        break
                return ([run[0]], hand)

    return None

def check_four_of_a_kind(rank_counts, cards):
    """Return [quad_rank, kicker] or None. Also returns the cards"""
    quad_rank = next((r for r, c in rank_counts.items() if c == 4), None) #gets first rank with count 4 will equal to quad rank or else it will default to None
    if quad_rank is None: #exits function early since no quads
        return None

    quad_cards = [c for c in cards if c.value == quad_rank] #gets all the cards in quad

    kicker_card = max((c for c in cards if c.value != quad_rank), key=lambda c: c.value) #gets the highest card other than quads as kicker

    hand_cards = quad_cards + [kicker_card]
    tiebreakers = [quad_rank, kicker_card.value]

    return (tiebreakers, hand_cards)

def check_full_house(rank_counts, cards):
    """Return [triple_rank, pair_rank] or None. Also returns the cards"""
    triples = sorted([r for r, c in rank_counts.items() if c >= 3], reverse=True) #checks if triples are present, if not exit function
    if not triples:
        return None

    triple_rank = triples[0]

    pair_candidates = sorted([r for r, c in rank_counts.items() if c >= 2 and r != triple_rank], reverse=True) #checks for pair

    if pair_candidates: #select best pair
        pair_rank = pair_candidates[0]

    elif len(triples)>=2: #if no pair and 2 triples, take 2nd triple as pair
        pair_rank = triples[1]

    else: #exit function since no pair
        return None

    triple_cards = [c for c in cards if c.value == triple_rank][:3]
    pair_cards = [c for c in cards if c.value == pair_rank][:2]

    hand_cards = triple_cards + pair_cards
    tiebreakers = [triple_rank, pair_rank]

    return (tiebreakers, hand_cards)

def check_flush(suit_counts, cards):
    """Return top 5 ranks of flush, or None. Also returns the cards"""
    best_tiebreak = None
    best_cards = None

    for suit in suit_counts: #loops through all suits
        suited_cards = [c for c in cards if c.suit == suit] #checks if suited is less than 5, if yes it will check next suit
        if len(suited_cards) < 5:
            continue

        suited_cards.sort(key=lambda c: c.value, reverse=True)
        top5_cards = suited_cards[:5] #takes best 5 cards in suit
        top5_ranks = [c.value for c in top5_cards] #ranks of the best 5 cards

        if (best_tiebreak is None) or (top5_ranks > best_tiebreak):
            best_tiebreak = top5_ranks
            best_cards = top5_cards

    if best_tiebreak:
        return (best_tiebreak, best_cards)
    return None

def check_straight(cards):
    """Return top 5 ranks of straight, or None (Ace high or low). Also returns the cards"""
    ranks = sorted({c.value for c in cards}, reverse=True)

    if 14 in ranks:
        ranks.append(1)

    for i in range(len(ranks) - 4): #loop through all possible straights
        run = ranks[i:i + 5]

        if max(run) - min(run) == 4 and len(set(run))==5: #condition to check for straight
            needed = set(run)

            def matches(card): #function to check if card is in needed
                return (card.value in needed) or (card.value == 14 and 1 in needed)

            hand_cards = [] #empty list of final output
            for c in sorted(cards, key=lambda c: c.value, reverse=True): #loop to convert needed set into list of card objects
                if matches(c):
                    if c.value == 14 and 1 in needed: #special case for ace
                        needed.remove(1)
                    else:
                        needed.remove(c.value)
                    hand_cards.append(c)
                if len(hand_cards) == 5:
                    break

            return ([run[0]], hand_cards)

    return None

def check_three_of_a_kind(rank_counts, cards):
    """Return [triple_rank, kicker1, kicker2] or None. Also returns the cards"""
    triple_rank = next((r for r, c in sorted(rank_counts.items(), reverse=True) if c == 3), None) #checks for triple, if none exit function early

    if triple_rank is None:
        return None

    triple_cards = [c for c in cards if c.value == triple_rank][:3]

    kicker_candidates = sorted((c for c in cards if c.value != triple_rank), key=lambda c: c.value, reverse=True) #creates sorted set of all non-triple cards

    kicker_cards = []
    seen_ranks = set()
    for c in kicker_candidates:
        if c.value not in seen_ranks:
            kicker_cards.append(c)
            seen_ranks.add(c.value)
        if len(kicker_cards) == 2: #got the 2 highest kicker cards, now break loop
            break

    hand_cards = triple_cards + kicker_cards
    tiebreakers = [triple_rank] + [c.value for c in kicker_cards]

    return (tiebreakers, hand_cards)

def check_two_pair(rank_counts, cards):
    """Return [high_pair, low_pair, kicker] or None. Also returns the cards"""
    pair_ranks = [r for r, c in rank_counts.items() if c >= 2] #finds all pairs
    if len(pair_ranks) < 2: #condition to check if pairs are less than 2, if true then exit function early
        return None

    pair_ranks.sort(reverse=True)
    high_pair, low_pair = pair_ranks[:2] #get high pair and low pair

    kicker_card = max((c for c in cards if c.value not in (high_pair, low_pair)), key=lambda c: c.value) #get highest kicker that is not a rank in high or low pair

    high_pair_cards = [c for c in cards if c.value == high_pair][:2]
    low_pair_cards = [c for c in cards if c.value == low_pair][:2]

    hand_cards = high_pair_cards + low_pair_cards +[kicker_card]
    tiebreaker = [high_pair, low_pair, kicker_card.value]

    return(tiebreaker, hand_cards)

def check_one_pair(rank_counts, cards):
    """Return [pair_rank, kicker1, kicker2, kicker3] or None. Also returns the cards"""
    pair_rank = next((r for r, c in sorted(rank_counts.items(), reverse=True) if c >= 2), None) #check if pair exists, if not then exit function early
    if pair_rank is None:
        return None

    pair_cards = [c for c in cards if c.value == pair_rank][:2]

    kicker_candidates = sorted((c for c in cards if c.value != pair_rank), key=lambda c: c.value, reverse=True) #all cards that are not pair_rank

    kicker_cards = []
    seen_ranks = set()
    for c in kicker_candidates: #gets top 3 cards as kickers
        if c.value not in seen_ranks:
            kicker_cards.append(c)
            seen_ranks.add(c.value)
        if len(kicker_cards) == 3:
            break

    hand_cards = pair_cards + kicker_cards
    tiebreaker = [pair_rank] + [c.value for c in kicker_cards]

    return (tiebreaker, hand_cards)

def format_hand_result(rank_value, tiebreakers):
    """Turn a hand evaluation result into a readable string."""
    RANK_NAMES = {2:"Two", 3:"Three", 4:"Four", 5:"Five", 6:"Six", 7:"Seven", 8:"Eight", 9:"Nine", 10:"Ten", 11:"Jack", 12:"Queen", 13:"King", 14:"Ace"}
    def name_card(value):
        return RANK_NAMES.get(value, str(value))

    if rank_value == 8:
        if tiebreakers[0] == 14 and tiebreakers[1] == 13: #special case for royal flush
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
