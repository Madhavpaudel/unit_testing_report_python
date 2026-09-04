"""
STAGE 2 - Check and checkmate
--------------------------------
Run this after check detection, king-safety filtering (rejecting moves
that expose or leave your own king in check), and checkmate detection
are implemented.
Covers report test IDs: T10-T13.
"""

from chess_engine import ChessEngine
from test_utils import check, summary

print("=== STAGE 2: Check & checkmate (T10-T13) ===\n")

# T10 - king in check detection
e = ChessEngine()
e.board = [[None] * 8 for _ in range(8)]
e.board[7][4] = 'wK'
e.board[0][4] = 'bR'
check("T10 detects check", e.is_in_check('w'))

# T11 - move into check rejected
e = ChessEngine()
e.board = [[None] * 8 for _ in range(8)]
e.board[7][4] = 'wK'
e.board[0][3] = 'bR'  # rook covers d-file
e.turn = 'w'
ok, info = e.make_move(7, 4, 7, 3)  # king e1-d1 walks into rook's file
check("T11 move into check rejected", not ok)

# T12 - pinned piece cannot move and expose king
e = ChessEngine()
e.board = [[None] * 8 for _ in range(8)]
e.board[7][4] = 'wK'
e.board[5][4] = 'wB'  # bishop pinned on the e-file
e.board[0][4] = 'bR'
e.turn = 'w'
ok, info = e.make_move(5, 4, 5, 5)  # bishop steps off the e-file, exposing king
check("T12 pinned piece move rejected", not ok)

# T13 - checkmate detection (fool's mate)
e = ChessEngine()
e.make_move(6, 5, 5, 5)  # f2-f3
e.make_move(1, 4, 3, 4)  # e7-e5
e.make_move(6, 6, 4, 6)  # g2-g4
ok, info = e.make_move(0, 3, 4, 7)  # Qd8-h4#
check("T13 checkmate detected", ok and e.is_checkmate('w') and e.game_over)

summary()
