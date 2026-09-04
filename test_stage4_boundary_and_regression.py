"""
STAGE 4 - Boundary conditions, invalid input, and final regression
-----------------------------------------------------------------------
Run this last, once every feature is implemented. Confirms the engine
rejects out-of-board coordinates safely, never corrupts board state on
an invalid move, and that ordinary movement still works correctly
after special-rule code (castling, en passant, promotion) has run -
i.e. this is the full regression pass referenced in report section 4.1.
Covers report test IDs: T21-T23.
"""

from chess_engine import ChessEngine
from test_utils import check, summary

print("=== STAGE 4: Boundary conditions & final regression (T21-T23) ===\n")

# T21 - board boundary
e = ChessEngine()
ok, info = e.make_move(6, 4, -1, 4)
check("T21 out-of-board destination rejected", not ok)

# T22 - state unchanged on invalid move
e = ChessEngine()
snapshot = [row[:] for row in e.board]
ok, info = e.make_move(7, 0, 6, 0)  # illegal friendly capture
check("T22 board state unchanged after invalid move", not ok and e.board == snapshot)

# T23 - regression: normal movement still works after a special move
e = ChessEngine()
e.board[7][5] = None
e.board[7][6] = None
e.make_move(7, 4, 7, 6)  # castle kingside
ok, info = e.make_move(1, 4, 3, 4)  # ordinary black pawn move afterwards
check("T23 regression - normal move after castling", ok and e.board[3][4] == 'bP')

summary()
