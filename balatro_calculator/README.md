# Balatro-Style Score Calculator

A poker-hand score calculator inspired by the scoring system in the game
*Balatro*: pick a 5-card hand, add jokers (order matters!), and see a full
step-by-step breakdown of how the final score is calculated.

Built as a **data-driven rules engine** rather than a hardcoded if/else
chain — each joker is declared once as *data* (a trigger condition + an
effect), and the scoring engine loops over whatever jokers it's given and
applies them generically. Adding a new joker means adding one entry to a
registry; the core scoring loop never changes. This "separate the rules from
the engine that runs them" pattern is the same idea behind pricing engines,
permission systems, and workflow automation tools more generally.

## Features

- Detects all standard poker hand types (Pair through Five of a Kind)
- Card enhancements (Bonus, Mult, Glass, Steel) and editions (Foil,
  Holographic, Polychrome)
- A registry-based joker system where jokers are plain data, not special-cased
  code, and where **joker order changes the result** (multiplicative and
  additive effects don't commute)
- A step-by-step score breakdown, so you can see exactly how a score was
  reached rather than just the final number
- A minimal REST API (FastAPI) and a zero-build-step HTML frontend
- Zero external dependencies for the core scoring logic — only the API/frontend
  layer needs anything installed

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

## Getting Started

Requires Python 3.9+.

The core logic has no external dependencies, so you can try it immediately:

```bash
git clone <this-repo-url>
cd balatro_calculator/src
python demo.py
```

This prints a few example hands with jokers applied, including a
demonstration of how joker order changes the final score.

### Running the tests

```bash
cd tests
python -m unittest test_hand_evaluator.py -v
python -m unittest test_scoring_engine.py -v
```

(Also runnable with `pytest`, which supports `unittest`-style tests without
any changes.)

### Running the full app (API + frontend)

```bash
pip install -r requirements.txt
cd src
uvicorn api:app --reload
```

Then open `frontend/index.html` in your browser (or serve it with
`python -m http.server` from the `frontend/` folder). Interactive API docs
are available at `http://localhost:8000/docs`.

## How the Scoring Pipeline Works

1. **Hand detection** (`hand_evaluator.py`) — given 5 cards, detect the hand
   type (Pair, Flush, Full House, etc.) and determine which cards count as
   "scoring cards" for that hand type.
2. **Base score** — look up base chips/mult for the detected hand type.
3. **Card modifiers** — each scoring card contributes its own chip value,
   plus any bonuses from its enhancement (Bonus, Mult, Glass, Steel) or
   edition (Foil, Holographic, Polychrome).
4. **Jokers, in order** — each joker's `trigger()` is checked against the
   current game state; if true, its `apply()` effect fires, **in the order
   the jokers are given**. See `test_joker_order_matters` in
   `tests/test_scoring_engine.py` for a concrete example (a x2 mult joker
   before a +10 mult joker gives a different result than the reverse order).
5. **Final score** = final chips × final mult.

Every step is recorded, so the breakdown can be displayed incrementally
rather than just as a final number.

## Roadmap

Ideas for extending this project, roughly in order of difficulty:

- **More jokers** — add entries to `JOKER_REGISTRY` in `jokers.py`, covering
  a range of `EffectType`s and trigger conditions.
- **New effect types** — e.g. a mult bonus that scales per scoring card (see
  the `Steady Hand` comment in `jokers.py` for where the current pattern
  needs extending).
- **More accurate scoring-card rules** — this project simplifies which cards
  count in a Full House / Flush (currently all 5 score). Real Balatro has
  more specific scoring-subset rules.
- **Retrigger effects** — some jokers make a card score twice, which needs
  `_apply_card_modifiers` restructured to support repeating a card's scoring.
- **Persistence** — save/load a chosen hand + joker list (SQLite is enough).
- **Deployment** — backend to Railway/Render, frontend to Vercel/Netlify, or
  serve the static HTML from the same backend.
- **Frontend polish** — the included `index.html` is intentionally minimal;
  a richer UI (visual card picker, drag-to-reorder jokers) would help a lot.

Contributions and forks along any of these lines are welcome.

## Contributing

Issues and pull requests are welcome. If you're adding jokers, please write
original names/descriptions rather than copying text from the source game
(see Disclaimer below).

## Disclaimer

Poker hand mechanics and chip/mult-style scoring are game rules, not
copyrightable expression, but this project is a fan-made, non-commercial
tribute — it is not affiliated with or endorsed by the creators of *Balatro*.
Joker names, descriptions, and flavor text here are written originally for
this project rather than copied from the source game. If you extend this
project, please continue writing your own descriptions and values rather
than copying text or art assets directly.

## License

MIT — see [LICENSE](LICENSE) for details.
