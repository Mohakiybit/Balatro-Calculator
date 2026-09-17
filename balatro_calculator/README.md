# Balatro-Style Score Calculator

A poker-hand score calculator inspired by the scoring system in the game
*Balatro*: pick a 5-card hand, add jokers (in order — order matters!), and see
a full step-by-step breakdown of how the final score is calculated.

This project is built as a **data-driven rules engine**, not a hardcoded
if/else chain. The main engineering idea worth understanding (and being able
to explain in an interview) is:

> Each joker is declared once as *data* (a trigger condition + an effect).
> The scoring engine loops over whatever jokers it's given and applies them
> generically. Adding a new joker means adding one entry to a registry —
> it never requires touching the core scoring loop.

This pattern (separating data from the engine that processes it) shows up
constantly in real software: pricing/discount engines, permission systems,
game engines, workflow automation tools, etc. It's a good thing to be able to
talk through in interviews.

## Project Structure

```
balatro_calculator/
├── src/
│   ├── models.py          # Card, Suit, Rank, HandType, ScoreResult data classes
│   ├── hand_evaluator.py  # detects hand type (Pair, Flush, etc.) from 5 cards
│   ├── jokers.py          # data-driven joker registry + effect application
│   ├── scoring_engine.py  # orchestrates: hand -> card mods -> jokers -> final score
│   ├── api.py             # FastAPI wrapper exposing the engine as a REST API
│   └── demo.py            # CLI script showing example scoring runs (no API needed)
├── tests/
│   ├── test_hand_evaluator.py
│   └── test_scoring_engine.py
├── frontend/
│   └── index.html         # plain HTML/JS UI (no build step required)
├── requirements.txt
└── README.md
```

## Quick Start (no setup required)

The core logic has **zero external dependencies** — you can see it working
immediately:

```bash
cd src
python demo.py
```

This prints a few example hands with jokers applied, showing the full
step-by-step breakdown, including a demonstration of how joker **order**
changes the final score.

## Running the Tests

Tests use Python's built-in `unittest`, so no extra install is needed either:

```bash
cd tests
python -m unittest test_hand_evaluator.py -v
python -m unittest test_scoring_engine.py -v
```

(You can also run them with `pytest` once installed — pytest can run
unittest-style tests without modification.)

## Running the Full App (API + frontend)

```bash
pip install -r requirements.txt
cd src
uvicorn api:app --reload
```

Then open `frontend/index.html` directly in your browser (or serve it with
`python -m http.server` from the `frontend/` folder). Visit
`http://localhost:8000/docs` for interactive API documentation (generated
automatically by FastAPI — worth screenshotting for your own README/resume).

## How the Scoring Pipeline Works

1. **Hand detection** (`hand_evaluator.py`): given 5 cards, detect the hand
   type (Pair, Flush, Full House, etc.) and determine which specific cards
   count as "scoring cards" for that hand type.
2. **Base score**: look up base chips/mult for the detected hand type.
3. **Card modifiers**: each scoring card contributes its own chip value, plus
   any bonuses from its enhancement (Bonus, Mult, Glass, Steel) or edition
   (Foil, Holographic, Polychrome).
4. **Jokers, in order**: each joker's `trigger()` is checked against the
   current game state; if true, its `apply()` effect fires. This happens
   **in the order the jokers are given** — see `test_joker_order_matters` in
   `tests/test_scoring_engine.py` for a concrete example of why this matters
   (a x2 mult joker before a +10 mult joker gives a different result than
   the reverse order).
5. **Final score** = final chips × final mult.

Every step is recorded so the UI can show a running total after each one —
this "show your work" breakdown is the most demoable part of the project.

## How to Extend This

This is meant as a **base**, not a finished product. Good next steps, roughly
in order of difficulty:

1. **Add more jokers.** Open `jokers.py` and add entries to `JOKER_REGISTRY`.
   Try to cover a range of `EffectType`s and trigger conditions. Aim for
   15-25 total for a portfolio-ready version.
2. **Add a new `EffectType`.** For example, a mult bonus that scales per
   scoring card (see the `Steady Hand` comment in `jokers.py` for a hint on
   where this pattern breaks down and needs extending).
3. **More accurate scoring-card rules.** This project simplifies which cards
   count in a Full House / Flush (it currently scores all 5). Real Balatro
   has more specific rules about scoring subsets — research these and adjust
   `hand_evaluator.py`.
4. **Retrigger effects.** Some jokers make a card score twice. This requires
   restructuring `_apply_card_modifiers` to support a "run this card's
   scoring twice" step — a good exercise in evolving your data model.
5. **Persistence (light CRUD).** Add a "save build" feature: store a chosen
   hand + joker list in a database (SQLite is fine) so users can save/load
   configurations. This is a good way to practice basic CRUD without making
   the whole project a CRUD app.
6. **Deploy it.** Backend to Railway/Render, frontend to Vercel/Netlify or
   just serve the static HTML from the same backend.
7. **Polish the frontend.** The included `index.html` is intentionally bare —
   consider rebuilding it in React if you want that on your resume, with a
   visual card picker instead of dropdowns.

## Notes on originality

Card/joker *mechanics* (poker hands, chip/mult scoring, joker-style modifier
systems) are game rules, not copyrightable expression — but the specific
joker names, descriptions, and flavor text here are written originally for
this project rather than copied from any source. If you extend this with
more jokers "inspired by" ones you remember from Balatro, keep writing your
own descriptions and values rather than copying text or art assets directly.
