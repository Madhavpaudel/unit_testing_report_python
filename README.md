# Chess Engine – Move Validation Only

A two-player, click-to-move chess GUI built with Python's `tkinter`, backed
by a move-validation engine with no AI opponent — matching the scope in the
PRT582 assessment report.

## Files

- `chess_engine.py` — the engine: board representation, legal move
  generation for all six piece types, check / checkmate / stalemate
  detection, castling, en passant, and promotion. No GUI dependencies,
  so it can be tested on its own.
- `chess_gui.py` — the `tkinter` GUI. Click a piece to see its legal
  moves highlighted, then click a highlighted square to move.
- `test_chess_engine.py` — automated tests aligned with the report's
  test IDs (T01–T23): initial setup, basic movement, blocked/illegal
  moves, check, pinned pieces, checkmate, castling (including through
  check and after the king has moved), en passant (valid and expired),
  promotion (including an invalid choice), board-boundary rejection,
  state-unchanged-on-invalid-move, and a regression check after a
  special move.

## Running it

Requires Python 3 with `tkinter` (bundled with most standard Python
installs; on some Linux distros install it separately, e.g.
`sudo apt install python3-tk`).

```bash
python3 chess_gui.py
```

Run the full automated test suite (no GUI required):

```bash
python3 test_chess_engine.py
```

All 26 checks currently pass.

### Staged tests, for section 7 "Test Execution Evidence"

The same 26 checks are also split into four smaller files that mirror
the four stages your report's section 7 asks for screenshots of. Run
them one at a time, in order, and screenshot each terminal output
separately:

```bash
python3 test_stage1_basic_movement.py            # T01-T09  (board setup, basic movement)
python3 test_stage2_check_checkmate.py            # T10-T13  (check & checkmate)
python3 test_stage3_special_moves.py              # T14-T20  (castling, en passant, promotion)
python3 test_stage4_boundary_and_regression.py    # T21-T23  (boundary conditions & final regression)
```

`test_stage4_boundary_and_regression.py` doubles as your "final full
regression test run" screenshot, since T23 specifically re-checks that
ordinary movement still works after castling code has run.

Note: because these stages all run against the finished engine, they
represent "after each feature was implemented" rather than a literal
"before any code existed" screenshot. If your report requires genuine
before-implementation evidence, that has to come from your own local
history (e.g. a screenshot from before you had `chess_engine.py`
written, or a git commit log) — that's something only you can capture,
since it depends on your real development timeline.

### Seeing a genuine FAIL, for section 6.1 "Before-and-After Evidence"

```bash
python3 demo_failure_and_fix.py
```

This recreates a real defect (a rook move generator that forgets to
check piece colour, so it's willing to "capture" your own pieces),
shows the test that catches it printing `FAIL`, prints the one-line
fix, then re-runs the same test against the corrected engine and
shows `PASS`. Screenshot this output directly into section 6.1 — it
gives you an authentic before/after pair (buggy code → failing test →
fixed code → passing test) instead of a fabricated example.

If your own AI-assisted process produced a different real bug along
the way (worth checking your actual prompt/response history for one),
swap it in here instead — a defect you genuinely hit and fixed is
stronger evidence than a recreated one.

## What the engine does and does not do

- Does: validate legality of a proposed move under standard chess
  rules, maintain board state, detect check/checkmate/stalemate,
  handle castling, en passant, and pawn promotion.
- Does not: choose moves, evaluate positions, or play as an AI
  opponent — this is out of scope per the report (section 2, Scope).

## Mapping to the report

- Section 3.5 "Expected System Behaviours" items 1–18 are each
  exercised by at least one test in `test_chess_engine.py`.
- Section 4 "Initial Automated Test Suite" (T01–T23) is implemented
  directly as the test functions in that file.
- Sections 3.6/3.7 boundary and invalid-input scenarios (off-board
  coordinates, blocked sliding pieces, friendly captures, castling
  after king/rook moves, expired en passant, invalid promotion input)
  are all covered.

You can use this as the working implementation to pair with your
AI-assisted development log (section 5), before/after evidence
(section 6.1), and test-execution screenshots (section 7) — for
example, screenshot `test_chess_engine.py` running in a terminal for
your "before implementation" and "final regression" evidence.
