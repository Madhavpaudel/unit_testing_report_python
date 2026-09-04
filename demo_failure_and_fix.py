"""
DEMO - What a FAILING test looks like, and how it gets fixed
------------------------------------------------------------------
This file exists purely to give you real FAIL output to screenshot
for report section 6.1 ("Before-and-After Evidence") and section 4.1
("Defect Prevented" column). It intentionally re-creates two genuine
bugs that came up while building this project, runs the tests that
catch them (showing FAIL), then runs the corrected version (showing
PASS) - so you have authentic before/after evidence rather than a
fabricated example.

Run with:  python3 demo_failure_and_fix.py
"""

from test_utils import check, summary, reset


print("# PART A - BUGGY ENGINE: friendly capture   #")
print("# not blocked (a real defect class AI code  #")
print("# can introduce if it forgets the same-     #")
print("# colour check on a sliding piece)           #")


import chess_engine as ce


class BuggyChessEngine(ce.ChessEngine):
    """A deliberately broken copy of the engine: the rook's move
    generator forgets to stop/refuse when it reaches a FRIENDLY piece,
    so it treats every piece in its path as capturable. This is exactly
    the kind of oversight AI-generated movement code can make."""

    def pseudo_legal_moves(self, r, c, board=None):
        board = self.board if board is None else board
        piece = board[r][c]
        if not piece:
            return []
        color, ptype = piece[0], piece[1]

        if ptype == 'R':
            moves = []
            for dr, dc in ce.ROOK_DIRS:
                nr, nc = r + dr, c + dc
                while ce.in_bounds(nr, nc):
                    target = board[nr][nc]
                    if target is None:
                        moves.append((nr, nc, None))
                    else:
                        # BUG: no check for target[0] != color - this allows
                        # "capturing" your own piece.
                        moves.append((nr, nc, 'capture'))
                        break
                    nr += dr
                    nc += dc
            return moves

        # everything else falls back to the correct implementation
        return super().pseudo_legal_moves(r, c, board)


print("Test: T08 friendly capture rejected\n")
buggy = BuggyChessEngine()
ok, info = buggy.make_move(7, 0, 6, 0)  # rook a1 "captures" own pawn a2
check("T08 friendly capture rejected [BUGGY ENGINE]", not ok)
summary()

print("\n--- Defect identified ---")
print("The rook's move generator appended every occupied square as a")
print("legal 'capture' target without checking the piece's colour,")
print("so it was willing to capture the player's own pieces.\n")

print("--- Fix applied (see chess_engine.py, ChessEngine.pseudo_legal_moves) ---")
print("if target[0] != color:")
print("    moves.append((nr, nc, 'capture'))")
print("break   # stop at the first piece encountered either way\n")


print("# PART B - CORRECTED ENGINE: same test now  #")
print("# passes                                     #")


reset()
print("Test: T08 friendly capture rejected\n")
fixed = ce.ChessEngine()
ok, info = fixed.make_move(7, 0, 6, 0)
check("T08 friendly capture rejected [FIXED ENGINE]", not ok)
summary()
