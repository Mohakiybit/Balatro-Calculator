"""
demo.py
A simple CLI demo showing a full scoring run with the step-by-step breakdown.
Run this to see the engine in action without needing the API/frontend set up.

Usage:
    python demo.py
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from models import Card, Rank, Suit, Enhancement, Edition
from jokers import get_joker, list_jokers
from scoring_engine import calculate_score


def print_result(cards, joker_names):
    jokers = [get_joker(name) for name in joker_names]
    result = calculate_score(cards, jokers)

    print(f"\nHand: {[repr(c) for c in cards]}")
    print(f"Jokers (in order): {joker_names}")
    print(f"Detected hand type: {result.hand_type.value}")
    print("-" * 60)
    for i, step in enumerate(result.steps, 1):
        print(f"  {i}. {step.description}")
        print(f"     -> running total: {step.chips:.0f} chips x {step.mult:.1f} mult")
    print("-" * 60)
    print(f"FINAL SCORE: {result.final_chips:.0f} chips x {result.final_mult:.1f} mult "
          f"= {result.total_score}")
    print("=" * 60)


if __name__ == "__main__":
    print("Available jokers:", list_jokers())

    # Example 1: a flush with a couple of jokers
    flush_hand = [
        Card(Rank.TWO, Suit.HEARTS), Card(Rank.FIVE, Suit.HEARTS),
        Card(Rank.SEVEN, Suit.HEARTS), Card(Rank.NINE, Suit.HEARTS),
        Card(Rank.JACK, Suit.HEARTS, edition=Edition.FOIL),
    ]
    print_result(flush_hand, ["Greedy Sage", "Basic Joker"])

    # Example 2: full house with order-sensitive jokers
    full_house_hand = [
        Card(Rank.TEN, Suit.HEARTS), Card(Rank.TEN, Suit.CLUBS),
        Card(Rank.TEN, Suit.DIAMONDS), Card(Rank.SIX, Suit.SPADES),
        Card(Rank.SIX, Suit.HEARTS),
    ]
    print_result(full_house_hand, ["Basic Joker", "Full House Fanatic"])
    print_result(full_house_hand, ["Full House Fanatic", "Basic Joker"])
