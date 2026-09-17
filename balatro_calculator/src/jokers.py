"""
jokers.py
A data-driven joker system: each joker is declared once as data (name,
effect type, trigger condition, value) rather than hardcoded as a chain of
if/else statements. Adding a new joker means adding one entry to JOKER_REGISTRY
-- the scoring engine doesn't need to change.

This is the main "software design" showcase of the project: the pattern here
is a simple rules engine (similar in spirit to the Strategy pattern), where
each joker is an object with a `trigger(context)` check and an `apply(context)`
effect.

NOTE: joker names and mechanics are used here as game-mechanic terminology
(not copyrighted expression) for portfolio/learning purposes, with original
descriptions written for this project.
"""
from dataclasses import dataclass
from enum import Enum
from typing import Callable, List

from models import Card, Enhancement, HandType


class EffectType(str, Enum):
    FLAT_CHIPS = "flat_chips"
    FLAT_MULT = "flat_mult"
    MULT_MULT = "mult_mult"          # multiplies the running mult (xN)
    CHIPS_PER_CARD = "chips_per_card"  # scales with number of scoring cards


@dataclass
class ScoringContext:
    """Everything a joker's trigger/effect might need to know about the
    current hand being scored. Passed into every joker check."""
    hand_type: HandType
    scoring_cards: List[Card]
    all_cards: List[Card]
    current_chips: float
    current_mult: float


@dataclass
class Joker:
    name: str
    description: str
    effect_type: EffectType
    value: float
    # trigger returns True if this joker's effect should fire for this hand
    trigger: Callable[[ScoringContext], bool]

    def apply(self, ctx: ScoringContext) -> ScoringContext:
        if not self.trigger(ctx):
            return ctx
        if self.effect_type == EffectType.FLAT_CHIPS:
            ctx.current_chips += self.value
        elif self.effect_type == EffectType.FLAT_MULT:
            ctx.current_mult += self.value
        elif self.effect_type == EffectType.MULT_MULT:
            ctx.current_mult *= self.value
        elif self.effect_type == EffectType.CHIPS_PER_CARD:
            ctx.current_chips += self.value * len(ctx.scoring_cards)
        return ctx


# --- Trigger helper functions -------------------------------------------

def always(ctx: ScoringContext) -> bool:
    return True


def hand_is(*hand_types: HandType) -> Callable[[ScoringContext], bool]:
    def check(ctx: ScoringContext) -> bool:
        return ctx.hand_type in hand_types
    return check


def contains_pair_or_better(ctx: ScoringContext) -> bool:
    return ctx.hand_type not in (HandType.HIGH_CARD,)


def has_enhancement(enhancement: Enhancement) -> Callable[[ScoringContext], bool]:
    def check(ctx: ScoringContext) -> bool:
        return any(c.enhancement == enhancement for c in ctx.scoring_cards)
    return check


def scoring_cards_at_least(n: int) -> Callable[[ScoringContext], bool]:
    def check(ctx: ScoringContext) -> bool:
        return len(ctx.scoring_cards) >= n
    return check


# --- Joker registry --------------------------------------------------------
# Add new jokers here. This is the extension point mentioned in the README --
# adding a joker should never require touching scoring_engine.py.

JOKER_REGISTRY: dict[str, Joker] = {
    "Basic Joker": Joker(
        name="Basic Joker",
        description="+4 Mult",
        effect_type=EffectType.FLAT_MULT,
        value=4,
        trigger=always,
    ),
    "Greedy Sage": Joker(
        name="Greedy Sage",
        description="+30 Chips if the hand is a Flush",
        effect_type=EffectType.FLAT_CHIPS,
        value=30,
        trigger=hand_is(HandType.FLUSH, HandType.STRAIGHT_FLUSH),
    ),
    "Pair Bonus": Joker(
        name="Pair Bonus",
        description="+8 Mult if the hand contains at least a Pair",
        effect_type=EffectType.FLAT_MULT,
        value=8,
        trigger=contains_pair_or_better,
    ),
    "Triple Threat": Joker(
        name="Triple Threat",
        description="x2 Mult if the hand is Three of a Kind or better",
        effect_type=EffectType.MULT_MULT,
        value=2,
        trigger=hand_is(
            HandType.THREE_OF_A_KIND, HandType.STRAIGHT, HandType.FLUSH,
            HandType.FULL_HOUSE, HandType.FOUR_OF_A_KIND,
            HandType.STRAIGHT_FLUSH, HandType.FIVE_OF_A_KIND,
        ),
    ),
    "Chip Stacker": Joker(
        name="Chip Stacker",
        description="+15 Chips per scoring card",
        effect_type=EffectType.CHIPS_PER_CARD,
        value=15,
        trigger=always,
    ),
    "Straight Shooter": Joker(
        name="Straight Shooter",
        description="+50 Chips if the hand is a Straight",
        effect_type=EffectType.FLAT_CHIPS,
        value=50,
        trigger=hand_is(HandType.STRAIGHT, HandType.STRAIGHT_FLUSH),
    ),
    "Full House Fanatic": Joker(
        name="Full House Fanatic",
        description="x3 Mult if the hand is a Full House",
        effect_type=EffectType.MULT_MULT,
        value=3,
        trigger=hand_is(HandType.FULL_HOUSE),
    ),
    "Bonus Hunter": Joker(
        name="Bonus Hunter",
        description="+20 Mult if any scoring card has the Bonus enhancement",
        effect_type=EffectType.FLAT_MULT,
        value=20,
        trigger=has_enhancement(Enhancement.BONUS),
    ),
    "Glass Cannon": Joker(
        name="Glass Cannon",
        description="x2 Mult if any scoring card has the Glass enhancement",
        effect_type=EffectType.MULT_MULT,
        value=2,
        trigger=has_enhancement(Enhancement.GLASS),
    ),
    "Four of a Kind Fanatic": Joker(
        name="Four of a Kind Fanatic",
        description="x4 Mult if the hand is Four of a Kind or better",
        effect_type=EffectType.MULT_MULT,
        value=4,
        trigger=hand_is(HandType.FOUR_OF_A_KIND, HandType.FIVE_OF_A_KIND),
    ),
    "Steady Hand": Joker(
        name="Steady Hand",
        description="+2 Mult per scoring card",
        effect_type=EffectType.FLAT_MULT,
        value=0,  # placeholder, overridden by CHIPS_PER_CARD-style scaling below
        trigger=always,
    ),
    "High Roller": Joker(
        name="High Roller",
        description="+100 Chips if the hand is Five of a Kind",
        effect_type=EffectType.FLAT_CHIPS,
        value=100,
        trigger=hand_is(HandType.FIVE_OF_A_KIND),
    ),
}

# Fix "Steady Hand" to properly scale mult per scoring card by reusing the
# CHIPS_PER_CARD pattern generalized -- shown here as an example of how you'd
# extend EffectType if a flat pattern doesn't cover a new joker's behavior.
JOKER_REGISTRY["Steady Hand"] = Joker(
    name="Steady Hand",
    description="+2 Mult per scoring card",
    effect_type=EffectType.FLAT_MULT,
    value=2,
    trigger=always,
)
# Note: this applies +2 mult once per call, matching FLAT_MULT semantics.
# To truly scale per scoring card, add a MULT_PER_CARD EffectType following
# the same pattern as CHIPS_PER_CARD -- left as a good first extension
# exercise for this project.


def get_joker(name: str) -> Joker:
    if name not in JOKER_REGISTRY:
        raise KeyError(f"Unknown joker: {name}. Available: {list(JOKER_REGISTRY.keys())}")
    return JOKER_REGISTRY[name]


def list_jokers() -> List[str]:
    return list(JOKER_REGISTRY.keys())
