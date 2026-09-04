from chess_engine import ChessEngine

passed = 0
failed = 0


def check(name, condition):
    global passed, failed
    if condition:
        passed += 1
        print(f"PASS {name}")
    else:
        failed += 1
        print(f"FAIL {name}")


# T01 - initial board setup
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

# T07 - bishop diagonal (after clearing pawn)
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
e.board[5][4] = 'wB'  # pretend bishop is pinned on e-file (use rook pin instead)
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
e.board[6][5] = None  # clear f2 pawn too, so the rook's file is unobstructed
e.board[1][5] = None
e.board[0][5] = None
e.board[3][5] = 'bR'  # rook attacks f1, the square the king passes through
ok, info = e.make_move(7, 4, 7, 6)
check("T15 castling through check rejected", not ok)

# T16 - moved king forfeits castling
e = ChessEngine()
e.board[7][5] = None
e.board[7][6] = None
e.make_move(7, 4, 7, 5)  # king e1-f1 (turn w), then move back
e.turn = 'w'
e.make_move(7, 5, 7, 4)  # king f1-e1, king_moved should already be True
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
e.make_move(1, 0, 2, 0)  # a7-a6 (en passant window on d-file has now expired)
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

# T20 - invalid promotion choice falls back safely (engine defends against bad input)
e = ChessEngine()
e.board = [[None] * 8 for _ in range(8)]
e.board[7][4] = 'wK'
e.board[0][4] = 'bK'
e.board[1][0] = 'wP'
e.turn = 'w'
ok, info = e.make_move(1, 0, 0, 0, promotion_choice='X')
check("T20 invalid promotion choice defaults to queen", ok and e.board[0][0] == 'wQ')

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

print(f"\n{passed} passed, {failed} failed")
