"""
scoring_engine.py
Orchestrates the full scoring pipeline in order:
  1. Detect hand type -> base chips/mult
  2. Apply per-card enhancement/edition bonuses for each scoring card
  3. Apply jokers in the order provided (order matters!)
  4. Final score = chips * mult

Produces a ScoreResult with a step-by-step breakdown for the UI.
"""
from typing import List

from hand_evaluator import evaluate_hand
from jokers import Joker, ScoringContext
from models import (
    Card, Edition, Enhancement, HAND_BASE_SCORES, ScoreResult, ScoreStep,
)


def _apply_card_modifiers(scoring_cards: List[Card], chips: float, mult: float):
    """Applies enhancement/edition bonuses for each scoring card and returns
    (new_chips, new_mult, list_of_step_descriptions)."""
    steps = []
    for card in scoring_cards:
        # Card's own chip value always contributes when it scores
        chips += card.rank.chip_value
        steps.append(f"{card!r} scores: +{card.rank.chip_value} chips")

        if card.enhancement == Enhancement.BONUS:
            chips += 30
            steps.append(f"{card!r} Bonus enhancement: +30 chips")
        elif card.enhancement == Enhancement.MULT:
            mult += 4
            steps.append(f"{card!r} Mult enhancement: +4 mult")
        elif card.enhancement == Enhancement.GLASS:
            mult *= 2
            steps.append(f"{card!r} Glass enhancement: x2 mult")
        elif card.enhancement == Enhancement.STEEL:
            mult *= 1.5
            steps.append(f"{card!r} Steel enhancement: x1.5 mult")

        if card.edition == Edition.FOIL:
            chips += 50
            steps.append(f"{card!r} Foil edition: +50 chips")
        elif card.edition == Edition.HOLOGRAPHIC:
            mult += 10
            steps.append(f"{card!r} Holographic edition: +10 mult")
        elif card.edition == Edition.POLYCHROME:
            mult *= 1.5
            steps.append(f"{card!r} Polychrome edition: x1.5 mult")

    return chips, mult, steps


def calculate_score(cards: List[Card], jokers: List[Joker]) -> ScoreResult:
    """
    cards: exactly 5 Card objects forming the played hand
    jokers: list of Joker objects, applied IN ORDER (left to right) -- order
            matters, e.g. a x2 Mult joker placed before a +10 Mult joker
            gives a different result than placing it after.
    """
    hand_type, scoring_cards = evaluate_hand(cards)
    base_chips, base_mult = HAND_BASE_SCORES[hand_type]

    result = ScoreResult(hand_type=hand_type)
    result.steps.append(ScoreStep(
        description=f"Base for {hand_type.value}: {base_chips} chips, {base_mult} mult",
        chips=base_chips, mult=base_mult,
    ))

    chips, mult = float(base_chips), float(base_mult)

    chips, mult, card_step_descriptions = _apply_card_modifiers(scoring_cards, chips, mult)
    for desc in card_step_descriptions:
        result.steps.append(ScoreStep(description=desc, chips=chips, mult=mult))

    ctx = ScoringContext(
        hand_type=hand_type,
        scoring_cards=scoring_cards,
        all_cards=cards,
        current_chips=chips,
        current_mult=mult,
    )

    for joker in jokers:
        before_chips, before_mult = ctx.current_chips, ctx.current_mult
        ctx = joker.apply(ctx)
        if ctx.current_chips != before_chips or ctx.current_mult != before_mult:
            result.steps.append(ScoreStep(
                description=f"{joker.name} ({joker.description}) triggers",
                chips=ctx.current_chips, mult=ctx.current_mult,
            ))
        else:
            result.steps.append(ScoreStep(
                description=f"{joker.name}: condition not met, no effect",
                chips=ctx.current_chips, mult=ctx.current_mult,
            ))

    result.final_chips = ctx.current_chips
    result.final_mult = ctx.current_mult
    return result
