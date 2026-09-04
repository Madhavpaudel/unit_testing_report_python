"""
STAGE 3 - Castling, en passant and promotion
------------------------------------------------
Run this after the three special-rule features are implemented:
castling (kingside/queenside, including the through-check and
already-moved rejection cases), en passant (valid and expired), and
pawn promotion (including an invalid promotion choice).
Covers report test IDs: T14-T20.
"""

from chess_engine import ChessEngine
from test_utils import check, summary

print("=== STAGE 3: Castling, en passant & promotion (T14-T20) ===\n")

# T14 - legal kingside castling
e = ChessEngine()
e.board[7][5] = None  # clear bishop f1
e.board[7][6] = None  # clear knight g1
ok, info = e.make_move(7, 4, 7, 6)
check("T14 legal castling accepted", ok and info['flag'] == 'castleK'
      and e.board[7][5] == 'wR' and e.board[7][6] == 'wK')

# T15 - castling through check rejected
e = ChessEngine()
e.board[7][5] = None
e.board[7][6] = None
e.board[6][5] = None  # clear f2 pawn so the attacking rook's file is unobstructed
e.board[1][5] = None
e.board[0][5] = None
e.board[3][5] = 'bR'  # rook attacks f1, the square the king passes through
ok, info = e.make_move(7, 4, 7, 6)
check("T15 castling through check rejected", not ok)

# T16 - moved king forfeits castling
e = ChessEngine()
e.board[7][5] = None
e.board[7][6] = None
e.make_move(7, 4, 7, 5)  # king e1-f1
e.turn = 'w'
e.make_move(7, 5, 7, 4)  # king f1-e1 (king_moved is already True)
ok, info = e.make_move(7, 4, 7, 6)
check("T16 castling rejected after king moved", not ok)

# T17 - valid en passant
e = ChessEngine()
e.make_move(6, 4, 4, 4)  # e2-e4
e.make_move(1, 0, 2, 0)  # a7-a6 (black waiting move)
e.make_move(4, 4, 3, 4)  # e4-e5
ok, info = e.make_move(1, 3, 3, 3)  # d7-d5 (creates en passant target)
check("setup d7-d5", ok)
ok, info = e.make_move(3, 4, 2, 3)  # e5xd6 en passant
check("T17 valid en passant accepted", ok and info['flag'] == 'ep' and e.board[3][3] is None)

# T18 - expired en passant rejected
e = ChessEngine()
e.make_move(6, 4, 4, 4)  # e2-e4
e.make_move(1, 3, 3, 3)  # d7-d5
e.make_move(4, 4, 3, 4)  # e4-e5
e.make_move(1, 0, 2, 0)  # a7-a6 (window on the d-file has now expired)
ok, info = e.make_move(3, 4, 2, 3)
check("T18 expired en passant rejected", not ok)

# T19 - promotion
e = ChessEngine()
e.board = [[None] * 8 for _ in range(8)]
e.board[7][4] = 'wK'
e.board[0][4] = 'bK'
e.board[1][0] = 'wP'
e.turn = 'w'
ok, info = e.make_move(1, 0, 0, 0, promotion_choice='Q')
check("T19 promotion to queen", ok and e.board[0][0] == 'wQ')

# T20 - invalid promotion choice defaults safely
e = ChessEngine()
e.board = [[None] * 8 for _ in range(8)]
e.board[7][4] = 'wK'
e.board[0][4] = 'bK'
e.board[1][0] = 'wP'
e.turn = 'w'
ok, info = e.make_move(1, 0, 0, 0, promotion_choice='X')
check("T20 invalid promotion choice defaults to queen", ok and e.board[0][0] == 'wQ')

summary()
