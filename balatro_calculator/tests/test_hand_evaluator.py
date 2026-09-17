import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from models import Card, Rank, Suit, HandType
from hand_evaluator import evaluate_hand


class TestHandEvaluator(unittest.TestCase):
    def test_high_card(self):
        cards = [
            Card(Rank.TWO, Suit.HEARTS), Card(Rank.FIVE, Suit.CLUBS),
            Card(Rank.SEVEN, Suit.DIAMONDS), Card(Rank.NINE, Suit.SPADES),
            Card(Rank.JACK, Suit.HEARTS),
        ]
        hand_type, scoring = evaluate_hand(cards)
        self.assertEqual(hand_type, HandType.HIGH_CARD)
        self.assertEqual(len(scoring), 1)
        self.assertEqual(scoring[0].rank, Rank.JACK)

    def test_pair(self):
        cards = [
            Card(Rank.TEN, Suit.HEARTS), Card(Rank.TEN, Suit.CLUBS),
            Card(Rank.THREE, Suit.DIAMONDS), Card(Rank.SIX, Suit.SPADES),
            Card(Rank.NINE, Suit.HEARTS),
        ]
        hand_type, scoring = evaluate_hand(cards)
        self.assertEqual(hand_type, HandType.PAIR)
        self.assertEqual(len(scoring), 2)

    def test_two_pair(self):
        cards = [
            Card(Rank.TEN, Suit.HEARTS), Card(Rank.TEN, Suit.CLUBS),
            Card(Rank.THREE, Suit.DIAMONDS), Card(Rank.THREE, Suit.SPADES),
            Card(Rank.NINE, Suit.HEARTS),
        ]
        hand_type, scoring = evaluate_hand(cards)
        self.assertEqual(hand_type, HandType.TWO_PAIR)
        self.assertEqual(len(scoring), 4)

    def test_three_of_a_kind(self):
        cards = [
            Card(Rank.TEN, Suit.HEARTS), Card(Rank.TEN, Suit.CLUBS),
            Card(Rank.TEN, Suit.DIAMONDS), Card(Rank.SIX, Suit.SPADES),
            Card(Rank.NINE, Suit.HEARTS),
        ]
        hand_type, scoring = evaluate_hand(cards)
        self.assertEqual(hand_type, HandType.THREE_OF_A_KIND)
        self.assertEqual(len(scoring), 3)

    def test_straight(self):
        cards = [
            Card(Rank.FIVE, Suit.HEARTS), Card(Rank.SIX, Suit.CLUBS),
            Card(Rank.SEVEN, Suit.DIAMONDS), Card(Rank.EIGHT, Suit.SPADES),
            Card(Rank.NINE, Suit.HEARTS),
        ]
        hand_type, scoring = evaluate_hand(cards)
        self.assertEqual(hand_type, HandType.STRAIGHT)
        self.assertEqual(len(scoring), 5)

    def test_ace_low_straight(self):
        cards = [
            Card(Rank.ACE, Suit.HEARTS), Card(Rank.TWO, Suit.CLUBS),
            Card(Rank.THREE, Suit.DIAMONDS), Card(Rank.FOUR, Suit.SPADES),
            Card(Rank.FIVE, Suit.HEARTS),
        ]
        hand_type, scoring = evaluate_hand(cards)
        self.assertEqual(hand_type, HandType.STRAIGHT)

    def test_flush(self):
        cards = [
            Card(Rank.TWO, Suit.HEARTS), Card(Rank.FIVE, Suit.HEARTS),
            Card(Rank.SEVEN, Suit.HEARTS), Card(Rank.NINE, Suit.HEARTS),
            Card(Rank.JACK, Suit.HEARTS),
        ]
        hand_type, scoring = evaluate_hand(cards)
        self.assertEqual(hand_type, HandType.FLUSH)
        self.assertEqual(len(scoring), 5)

    def test_full_house(self):
        cards = [
            Card(Rank.TEN, Suit.HEARTS), Card(Rank.TEN, Suit.CLUBS),
            Card(Rank.TEN, Suit.DIAMONDS), Card(Rank.SIX, Suit.SPADES),
            Card(Rank.SIX, Suit.HEARTS),
        ]
        hand_type, scoring = evaluate_hand(cards)
        self.assertEqual(hand_type, HandType.FULL_HOUSE)
        self.assertEqual(len(scoring), 5)

    def test_four_of_a_kind(self):
        cards = [
            Card(Rank.TEN, Suit.HEARTS), Card(Rank.TEN, Suit.CLUBS),
            Card(Rank.TEN, Suit.DIAMONDS), Card(Rank.TEN, Suit.SPADES),
            Card(Rank.NINE, Suit.HEARTS),
        ]
        hand_type, scoring = evaluate_hand(cards)
        self.assertEqual(hand_type, HandType.FOUR_OF_A_KIND)
        self.assertEqual(len(scoring), 4)

    def test_straight_flush(self):
        cards = [
            Card(Rank.FIVE, Suit.HEARTS), Card(Rank.SIX, Suit.HEARTS),
            Card(Rank.SEVEN, Suit.HEARTS), Card(Rank.EIGHT, Suit.HEARTS),
            Card(Rank.NINE, Suit.HEARTS),
        ]
        hand_type, scoring = evaluate_hand(cards)
        self.assertEqual(hand_type, HandType.STRAIGHT_FLUSH)

    def test_five_of_a_kind(self):
        # Only possible with enhanced decks in the real game, but the engine
        # should still detect it correctly given 5 same-rank cards.
        cards = [
            Card(Rank.TEN, Suit.HEARTS), Card(Rank.TEN, Suit.CLUBS),
            Card(Rank.TEN, Suit.DIAMONDS), Card(Rank.TEN, Suit.SPADES),
            Card(Rank.TEN, Suit.HEARTS),
        ]
        hand_type, scoring = evaluate_hand(cards)
        self.assertEqual(hand_type, HandType.FIVE_OF_A_KIND)

    def test_wrong_card_count_raises(self):
        cards = [Card(Rank.TEN, Suit.HEARTS)]
        with self.assertRaises(ValueError):
            evaluate_hand(cards)


if __name__ == "__main__":
    unittest.main()
