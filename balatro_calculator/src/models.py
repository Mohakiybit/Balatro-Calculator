"""
models.py
Core data structures for cards and hands. Kept dependency-free (no pydantic/
fastapi here) so this module can be unit tested in isolation and reused by
both the CLI, the API layer, and future extensions.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class Suit(str, Enum):
    HEARTS = "Hearts"
    DIAMONDS = "Diamonds"
    CLUBS = "Clubs"
    SPADES = "Spades"


class Rank(str, Enum):
    TWO = "2"
    THREE = "3"
    FOUR = "4"
    FIVE = "5"
    SIX = "6"
    SEVEN = "7"
    EIGHT = "8"
    NINE = "9"
    TEN = "10"
    JACK = "J"
    QUEEN = "Q"
    KING = "K"
    ACE = "A"

    @property
    def numeric_value(self) -> int:
        """Card rank value used for straights (Ace is high, 14)."""
        order = {
            Rank.TWO: 2, Rank.THREE: 3, Rank.FOUR: 4, Rank.FIVE: 5,
            Rank.SIX: 6, Rank.SEVEN: 7, Rank.EIGHT: 8, Rank.NINE: 9,
            Rank.TEN: 10, Rank.JACK: 11, Rank.QUEEN: 12, Rank.KING: 13,
            Rank.ACE: 14,
        }
        return order[self]

    @property
    def chip_value(self) -> int:
        """Base chip value a card contributes when it scores (face cards
        worth 10, Ace worth 11, numbers worth their number) — mirrors the
        base scoring convention used in Balatro-like scoring systems."""
        if self in (Rank.JACK, Rank.QUEEN, Rank.KING):
            return 10
        if self == Rank.ACE:
            return 11
        return int(self.value)


class Enhancement(str, Enum):
    """Card enhancements that modify how an individual card scores."""
    NONE = "None"
    BONUS = "Bonus"       # +30 chips when this card scores
    MULT = "Mult"         # +4 mult when this card scores
    GLASS = "Glass"       # x2 mult when this card scores
    STEEL = "Steel"       # x1.5 mult, applied at the multiplier stage
    GOLD = "Gold"         # no scoring bonus in this simplified model (real
                           # game grants money) — included for completeness


class Edition(str, Enum):
    """Card/joker editions that add flat or multiplicative bonuses."""
    NONE = "None"
    FOIL = "Foil"                 # +50 chips
    HOLOGRAPHIC = "Holographic"   # +10 mult
    POLYCHROME = "Polychrome"     # x1.5 mult


@dataclass(frozen=True)
class Card:
    rank: Rank
    suit: Suit
    enhancement: Enhancement = Enhancement.NONE
    edition: Edition = Edition.NONE

    def __repr__(self):
        tag = f" [{self.enhancement.value}]" if self.enhancement != Enhancement.NONE else ""
        ed = f" ({self.edition.value})" if self.edition != Edition.NONE else ""
        return f"{self.rank.value}{self.suit.value[0]}{tag}{ed}"


class HandType(str, Enum):
    HIGH_CARD = "High Card"
    PAIR = "Pair"
    TWO_PAIR = "Two Pair"
    THREE_OF_A_KIND = "Three of a Kind"
    STRAIGHT = "Straight"
    FLUSH = "Flush"
    FULL_HOUSE = "Full House"
    FOUR_OF_A_KIND = "Four of a Kind"
    STRAIGHT_FLUSH = "Straight Flush"
    FIVE_OF_A_KIND = "Five of a Kind"


# Base chips and mult granted purely by the detected hand type, before any
# card enhancements or jokers are applied. These numbers mirror the base
# values used in Balatro-like scoring systems.
HAND_BASE_SCORES = {
    HandType.HIGH_CARD: (5, 1),
    HandType.PAIR: (10, 2),
    HandType.TWO_PAIR: (20, 2),
    HandType.THREE_OF_A_KIND: (30, 3),
    HandType.STRAIGHT: (30, 4),
    HandType.FLUSH: (35, 4),
    HandType.FULL_HOUSE: (40, 4),
    HandType.FOUR_OF_A_KIND: (60, 7),
    HandType.STRAIGHT_FLUSH: (100, 8),
    HandType.FIVE_OF_A_KIND: (120, 12),
}


@dataclass
class ScoreStep:
    """A single line in the step-by-step score breakdown, used to build the
    'show your work' UI feature."""
    description: str
    chips: float
    mult: float


@dataclass
class ScoreResult:
    hand_type: HandType
    steps: List[ScoreStep] = field(default_factory=list)
    final_chips: float = 0.0
    final_mult: float = 0.0

    @property
    def total_score(self) -> int:
        return int(round(self.final_chips * self.final_mult))
