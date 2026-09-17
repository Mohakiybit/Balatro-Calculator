import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from models import Card, Rank, Suit, Enhancement, Edition, HandType
from jokers import get_joker
from scoring_engine import calculate_score


class TestScoringEngine(unittest.TestCase):
    def test_high_card_no_jokers(self):
        cards = [
            Card(Rank.TWO, Suit.HEARTS), Card(Rank.FIVE, Suit.CLUBS),
            Card(Rank.SEVEN, Suit.DIAMONDS), Card(Rank.NINE, Suit.SPADES),
            Card(Rank.JACK, Suit.HEARTS),
        ]
        result = calculate_score(cards, [])
        # Base High Card = 5 chips, 1 mult. Scoring card is Jack (10 chips).
        # Total chips = 5 + 10 = 15, mult = 1 -> score = 15
        self.assertEqual(result.hand_type, HandType.HIGH_CARD)
        self.assertEqual(result.total_score, 15)

    def test_pair_with_basic_joker(self):
        cards = [
            Card(Rank.TEN, Suit.HEARTS), Card(Rank.TEN, Suit.CLUBS),
            Card(Rank.THREE, Suit.DIAMONDS), Card(Rank.SIX, Suit.SPADES),
            Card(Rank.NINE, Suit.HEARTS),
        ]
        # Base Pair = 10 chips, 2 mult. Scoring cards: two Tens (10 chips each).
        # chips = 10 + 10 + 10 = 30, mult = 2 (before joker)
        # Basic Joker: +4 mult -> mult = 6
        # Final score = 30 * 6 = 180
        result = calculate_score(cards, [get_joker("Basic Joker")])
        self.assertEqual(result.total_score, 180)

    def test_joker_order_matters(self):
        """A x2 mult joker BEFORE a +10 flat mult joker should give a
        different result than the reverse order -- this is the core
        'order matters' behavior the project is meant to demonstrate."""
        cards = [
            Card(Rank.TEN, Suit.HEARTS), Card(Rank.TEN, Suit.CLUBS),
            Card(Rank.THREE, Suit.DIAMONDS), Card(Rank.SIX, Suit.SPADES),
            Card(Rank.NINE, Suit.HEARTS),
        ]
        # base mult = 2 before jokers (Pair)
        flat_plus_10 = get_joker("Basic Joker")  # +4 mult, reuse for simplicity
        mult_x2 = get_joker("Triple Threat")     # x2 mult, but only triggers
                                                   # on Three-of-a-Kind+, so use
                                                   # a manual joker instead for
                                                   # a controlled unit test:
        from jokers import Joker, EffectType, always
        x2 = Joker("TestX2", "x2 mult", EffectType.MULT_MULT, 2, always)
        plus10 = Joker("TestPlus10", "+10 mult", EffectType.FLAT_MULT, 10, always)

        result_x2_first = calculate_score(cards, [x2, plus10])
        result_plus10_first = calculate_score(cards, [plus10, x2])

        # base mult = 2
        # x2 first: (2*2)+10 = 14 -> chips 30 * 14 = 420
        # plus10 first: (2+10)*2 = 24 -> chips 30 * 24 = 720
        self.assertEqual(result_x2_first.total_score, 420)
        self.assertEqual(result_plus10_first.total_score, 720)
        self.assertNotEqual(result_x2_first.total_score, result_plus10_first.total_score)

    def test_card_enhancement_bonus(self):
        cards = [
            Card(Rank.TWO, Suit.HEARTS, enhancement=Enhancement.BONUS),
            Card(Rank.FIVE, Suit.CLUBS), Card(Rank.SEVEN, Suit.DIAMONDS),
            Card(Rank.NINE, Suit.SPADES), Card(Rank.JACK, Suit.HEARTS),
        ]
        # High card scores only the Jack (highest), so the Bonus on the Two
        # should NOT apply since the Two isn't a scoring card.
        result = calculate_score(cards, [])
        self.assertEqual(result.total_score, 15)  # unchanged from base test

    def test_card_enhancement_applies_when_scoring(self):
        cards = [
            Card(Rank.JACK, Suit.HEARTS, enhancement=Enhancement.BONUS),
            Card(Rank.FIVE, Suit.CLUBS), Card(Rank.SEVEN, Suit.DIAMONDS),
            Card(Rank.NINE, Suit.SPADES), Card(Rank.TWO, Suit.HEARTS),
        ]
        # High card scores the Jack (10 chips + 30 Bonus = 40), base chips 5
        # Total chips = 5 + 10 + 30 = 45, mult = 1 -> score 45
        result = calculate_score(cards, [])
        self.assertEqual(result.total_score, 45)

    def test_edition_polychrome_multiplies_mult(self):
        cards = [
            Card(Rank.JACK, Suit.HEARTS, edition=Edition.POLYCHROME),
            Card(Rank.FIVE, Suit.CLUBS), Card(Rank.SEVEN, Suit.DIAMONDS),
            Card(Rank.NINE, Suit.SPADES), Card(Rank.TWO, Suit.HEARTS),
        ]
        # High card: chips = 5 + 10 = 15, mult = 1 * 1.5 = 1.5
        # score = 15 * 1.5 = 22.5 -> rounds to 22 or 23 depending on rounding
        result = calculate_score(cards, [])
        self.assertEqual(result.final_chips, 15)
        self.assertEqual(result.final_mult, 1.5)

    def test_unknown_joker_raises(self):
        with self.assertRaises(KeyError):
            get_joker("Nonexistent Joker")

    def test_conditional_joker_no_effect_when_condition_unmet(self):
        cards = [
            Card(Rank.TWO, Suit.HEARTS), Card(Rank.FIVE, Suit.CLUBS),
            Card(Rank.SEVEN, Suit.DIAMONDS), Card(Rank.NINE, Suit.SPADES),
            Card(Rank.JACK, Suit.HEARTS),
        ]
        # "Full House Fanatic" only triggers on Full House; this is High Card,
        # so it should have zero effect.
        result = calculate_score(cards, [get_joker("Full House Fanatic")])
        self.assertEqual(result.total_score, 15)  # same as no-joker baseline


if __name__ == "__main__":
    unittest.main()
