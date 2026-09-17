"""
hand_evaluator.py
Detects the poker hand type from a list of Card objects and determines which
cards count as "scoring cards" for that hand (e.g., only the paired cards
score in a Pair; all 5 score in a Flush).

This is intentionally simplified for portfolio purposes: real Balatro scoring
subsets which cards count precisely, and has additional edge cases. Treat
`scoring_cards` here as an extension point -- see README for details on how
to make this more accurate.
"""
from collections import Counter
from typing import List, Tuple

from models import Card, HandType, Rank


def _is_straight(sorted_values: List[int]) -> bool:
    """Check for 5 consecutive ranks. Handles the Ace-low straight (A-2-3-4-5)
    as a special case, matching standard poker rules."""
    unique_sorted = sorted(set(sorted_values))
    if len(unique_sorted) != 5:
        return False
    if unique_sorted[-1] - unique_sorted[0] == 4:
        return True
    # Ace-low straight: A,2,3,4,5 -> values 14,2,3,4,5
    if unique_sorted == [2, 3, 4, 5, 14]:
        return True
    return False


def evaluate_hand(cards: List[Card]) -> Tuple[HandType, List[Card]]:
    """Returns (hand_type, scoring_cards)."""
    if len(cards) != 5:
        raise ValueError("Exactly 5 cards are required to evaluate a hand.")

    ranks = [c.rank for c in cards]
    suits = [c.suit for c in cards]
    values = [r.numeric_value for r in ranks]

    rank_counts = Counter(ranks)
    counts_sorted = sorted(rank_counts.values(), reverse=True)

    is_flush = len(set(suits)) == 1
    is_straight = _is_straight(values)

    def cards_with_rank(target_ranks):
        return [c for c in cards if c.rank in target_ranks]

    if is_straight and is_flush:
        return HandType.STRAIGHT_FLUSH, cards
    if counts_sorted == [5]:
        return HandType.FIVE_OF_A_KIND, cards
    if counts_sorted == [4, 1]:
        quad_rank = [r for r, c in rank_counts.items() if c == 4][0]
        return HandType.FOUR_OF_A_KIND, cards_with_rank({quad_rank})
    if counts_sorted == [3, 2]:
        return HandType.FULL_HOUSE, cards  # full house scores all 5 cards
    if is_flush:
        return HandType.FLUSH, cards
    if is_straight:
        return HandType.STRAIGHT, cards
    if counts_sorted == [3, 1, 1]:
        triple_rank = [r for r, c in rank_counts.items() if c == 3][0]
        return HandType.THREE_OF_A_KIND, cards_with_rank({triple_rank})
    if counts_sorted == [2, 2, 1]:
        pair_ranks = {r for r, c in rank_counts.items() if c == 2}
        return HandType.TWO_PAIR, cards_with_rank(pair_ranks)
    if counts_sorted == [2, 1, 1, 1]:
        pair_rank = [r for r, c in rank_counts.items() if c == 2][0]
        return HandType.PAIR, cards_with_rank({pair_rank})

    # High card: only the single highest-ranked card scores
    highest = max(cards, key=lambda c: c.rank.numeric_value)
    return HandType.HIGH_CARD, [highest]
