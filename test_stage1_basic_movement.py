"""
STAGE 1 - Initial board setup and basic piece movement
--------------------------------------------------------
Run this after the board representation and basic movement rules
(pawn, knight, bishop, rook, queen, king; captures; blocked paths;
friendly-capture rejection; turn enforcement) are implemented.
Covers report test IDs: T01-T09.
"""

from chess_engine import ChessEngine
from test_utils import check, summary

print("=== STAGE 1: Board setup & basic movement (T01-T09) ===\n")

# T01 - initial board
e = ChessEngine()
check("T01 initial board - white king", e.board[7][4] == 'wK')
check("T01 initial board - black queen", e.board[0][3] == 'bQ')
check("T01 initial board - pawn rows", all(e.board[6][c] == 'wP' for c in range(8)) and
      all(e.board[1][c] == 'bP' for c in range(8)))

# T02 - pawn one step
e = ChessEngine()
ok, info = e.make_move(6, 4, 5, 4)  # e2-e3
check("T02 pawn one-step", ok and e.board[5][4] == 'wP')

# T03 - pawn two step
e = ChessEngine()
ok, info = e.make_move(6, 4, 4, 4)  # e2-e4
check("T03 pawn two-step", ok and e.board[4][4] == 'wP' and e.en_passant_target == (5, 4))

# T04 - blocked pawn
e = ChessEngine()
e.board[5][4] = 'bP'  # block e3
ok, info = e.make_move(6, 4, 5, 4)
check("T04 blocked pawn rejected", not ok)

# T05 - rook path blocked
e = ChessEngine()
ok, info = e.make_move(7, 0, 5, 0)  # rook a1-a3 blocked by pawn a2
check("T05 rook blocked path rejected", not ok)

# T06 - knight jump
e = ChessEngine()
ok, info = e.make_move(7, 1, 5, 2)  # Nb1-c3
check("T06 knight jump accepted", ok and e.board[5][2] == 'wN')

# T07 - bishop diagonal
e = ChessEngine()
e.board[6][3] = None  # clear d2 pawn to free the c1 bishop's diagonal
ok, info = e.make_move(7, 2, 5, 4)  # Bc1-e3
check("T07 bishop diagonal accepted", ok and e.board[5][4] == 'wB')

# T08 - friendly capture rejected
e = ChessEngine()
ok, info = e.make_move(7, 0, 6, 0)  # rook a1 onto own pawn a2
check("T08 friendly capture rejected", not ok)

# T09 - wrong turn
e = ChessEngine()
ok, info = e.make_move(1, 4, 3, 4)  # black tries to move first
check("T09 wrong turn rejected", not ok)

summary()
