"""
api.py
FastAPI wrapper around the scoring engine. Exposes:
  GET  /jokers          -> list available jokers with descriptions
  GET  /cards/reference -> ranks, suits, enhancements, editions (for building
                            the frontend's dropdowns)
  POST /score           -> submit a hand + ordered joker list, get back the
                            full step-by-step ScoreResult

Run with:
    uvicorn api:app --reload

NOTE: this file requires `fastapi`, `uvicorn`, and `pydantic` (see
requirements.txt) which were not installable in the sandbox used to build
this project, so this file has been syntax-checked but not executed. Test it
locally after `pip install -r requirements.txt`.
"""
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from jokers import JOKER_REGISTRY, get_joker
from models import Card, Edition, Enhancement, Rank, Suit
from scoring_engine import calculate_score

app = FastAPI(title="Balatro Score Calculator API")

# Allow the frontend (served separately, e.g. from a different port or
# static host) to call this API during local development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class CardInput(BaseModel):
    rank: str          # e.g. "10", "J", "A"
    suit: str          # e.g. "Hearts"
    enhancement: str = "None"
    edition: str = "None"


class ScoreRequest(BaseModel):
    cards: List[CardInput]
    joker_names: List[str] = []  # order matters!


class StepOutput(BaseModel):
    description: str
    chips: float
    mult: float


class ScoreResponse(BaseModel):
    hand_type: str
    steps: List[StepOutput]
    final_chips: float
    final_mult: float
    total_score: int


def _to_card(card_input: CardInput) -> Card:
    try:
        rank = Rank(card_input.rank)
        suit = Suit(card_input.suit)
        enhancement = Enhancement(card_input.enhancement)
        edition = Edition(card_input.edition)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid card field: {e}")
    return Card(rank=rank, suit=suit, enhancement=enhancement, edition=edition)


@app.get("/jokers")
def list_jokers_endpoint():
    return [
        {"name": j.name, "description": j.description}
        for j in JOKER_REGISTRY.values()
    ]


@app.get("/cards/reference")
def cards_reference():
    return {
        "ranks": [r.value for r in Rank],
        "suits": [s.value for s in Suit],
        "enhancements": [e.value for e in Enhancement],
        "editions": [e.value for e in Edition],
    }


@app.post("/score", response_model=ScoreResponse)
def score_hand(request: ScoreRequest):
    if len(request.cards) != 5:
        raise HTTPException(status_code=400, detail="Exactly 5 cards are required.")

    cards = [_to_card(c) for c in request.cards]

    try:
        jokers = [get_joker(name) for name in request.joker_names]
    except KeyError as e:
        raise HTTPException(status_code=400, detail=str(e))

    result = calculate_score(cards, jokers)

    return ScoreResponse(
        hand_type=result.hand_type.value,
        steps=[StepOutput(description=s.description, chips=s.chips, mult=s.mult) for s in result.steps],
        final_chips=result.final_chips,
        final_mult=result.final_mult,
        total_score=result.total_score,
    )


@app.get("/")
def root():
    return {"message": "Balatro Score Calculator API. See /docs for interactive API documentation."}
