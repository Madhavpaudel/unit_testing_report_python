"""
Chess Engine - Move Validation Only
------------------------------------
Implements standard chess move legality: piece movement, captures,
check / checkmate / stalemate detection, castling, en passant and
pawn promotion. Deliberately contains NO evaluation function and NO
move-choosing logic - this engine only tells you whether a move is
legal and what the resulting board state is. Move selection / "AI
opponent" is explicitly out of scope (see assessment report, Scope).

Board coordinates: row 0 = rank 8 (top, Black's back rank),
                    row 7 = rank 1 (bottom, White's back rank),
                    col 0 = file a, col 7 = file h.

A square is either None (empty) or a two-character string:
    colour ('w' / 'b') + piece type ('P','N','B','R','Q','K')
"""

KNIGHT_DELTAS = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                 (1, -2), (1, 2), (2, -1), (2, 1)]
BISHOP_DIRS = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
ROOK_DIRS = [(-1, 0), (1, 0), (0, -1), (0, 1)]
QUEEN_DIRS = BISHOP_DIRS + ROOK_DIRS


def in_bounds(r, c):
    return 0 <= r < 8 and 0 <= c < 8


def other(color):
    return 'b' if color == 'w' else 'w'


class ChessEngine:
    def __init__(self):
        self.board = self._initial_board()
        self.turn = 'w'
        self.king_moved = {'w': False, 'b': False}
        # rook_moved tracked separately for kingside ('K') / queenside ('Q') rook
        self.rook_moved = {'w': {'K': False, 'Q': False},
                            'b': {'K': False, 'Q': False}}
        self.en_passant_target = None  # (row, col) square a pawn can capture onto
        self.move_log = []             # human-readable log of applied moves
        self.status = "White to move"
        self.game_over = False

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------
    def _initial_board(self):
        board = [[None] * 8 for _ in range(8)]
        back_rank = ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
        for c in range(8):
            board[0][c] = 'b' + back_rank[c]
            board[1][c] = 'bP'
            board[6][c] = 'wP'
            board[7][c] = 'w' + back_rank[c]
        return board

    def find_king(self, color, board=None):
        board = self.board if board is None else board
        for r in range(8):
            for c in range(8):
                p = board[r][c]
                if p == color + 'K':
                    return (r, c)
        return None

    # ------------------------------------------------------------------
    # Attack map (used for check detection and for filtering castling
    # / king moves). Sliding pieces stop at, and include, the first
    # occupied square in each direction - this correctly captures both
    # "this square can be captured" and "this square is defended".
    # ------------------------------------------------------------------
    def get_attacked_squares(self, color, board=None):
        board = self.board if board is None else board
        attacked = set()
        for r in range(8):
            for c in range(8):
                piece = board[r][c]
                if not piece or piece[0] != color:
                    continue
                ptype = piece[1]
                if ptype == 'P':
                    direction = -1 if color == 'w' else 1
                    for dc in (-1, 1):
                        nr, nc = r + direction, c + dc
                        if in_bounds(nr, nc):
                            attacked.add((nr, nc))
                elif ptype == 'N':
                    for dr, dc in KNIGHT_DELTAS:
                        nr, nc = r + dr, c + dc
                        if in_bounds(nr, nc):
                            attacked.add((nr, nc))
                elif ptype == 'K':
                    for dr in (-1, 0, 1):
                        for dc in (-1, 0, 1):
                            if dr == 0 and dc == 0:
                                continue
                            nr, nc = r + dr, c + dc
                            if in_bounds(nr, nc):
                                attacked.add((nr, nc))
                else:
                    dirs = BISHOP_DIRS if ptype == 'B' else ROOK_DIRS if ptype == 'R' else QUEEN_DIRS
                    for dr, dc in dirs:
                        nr, nc = r + dr, c + dc
                        while in_bounds(nr, nc):
                            attacked.add((nr, nc))
                            if board[nr][nc] is not None:
                                break
                            nr += dr
                            nc += dc
        return attacked

    def is_in_check(self, color, board=None):
        board = self.board if board is None else board
        king_pos = self.find_king(color, board)
        if king_pos is None:
            return False
        return king_pos in self.get_attacked_squares(other(color), board)

    # ------------------------------------------------------------------
    # Pseudo-legal move generation (movement-pattern legal, but does
    # NOT yet guarantee the mover's own king is safe afterwards)
    # ------------------------------------------------------------------
    def pseudo_legal_moves(self, r, c, board=None):
        board = self.board if board is None else board
        piece = board[r][c]
        if not piece:
            return []
        color, ptype = piece[0], piece[1]
        moves = []

        if ptype == 'P':
            direction = -1 if color == 'w' else 1
            start_row = 6 if color == 'w' else 1
            promo_row = 0 if color == 'w' else 7

            one_r = r + direction
            if in_bounds(one_r, c) and board[one_r][c] is None:
                flag = 'promo' if one_r == promo_row else None
                moves.append((one_r, c, flag))
                two_r = r + 2 * direction
                if r == start_row and board[two_r][c] is None:
                    moves.append((two_r, c, 'double'))

            for dc in (-1, 1):
                nr, nc = r + direction, c + dc
                if not in_bounds(nr, nc):
                    continue
                target = board[nr][nc]
                if target is not None and target[0] != color:
                    flag = 'capture_promo' if nr == promo_row else 'capture'
                    moves.append((nr, nc, flag))
                elif target is None and self.en_passant_target == (nr, nc):
                    moves.append((nr, nc, 'ep'))

        elif ptype == 'N':
            for dr, dc in KNIGHT_DELTAS:
                nr, nc = r + dr, c + dc
                if in_bounds(nr, nc):
                    target = board[nr][nc]
                    if target is None or target[0] != color:
                        moves.append((nr, nc, 'capture' if target else None))

        elif ptype == 'K':
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0:
                        continue
                    nr, nc = r + dr, c + dc
                    if in_bounds(nr, nc):
                        target = board[nr][nc]
                        if target is None or target[0] != color:
                            moves.append((nr, nc, 'capture' if target else None))

            # Castling
            if not self.king_moved[color]:
                opp_attacks = self.get_attacked_squares(other(color), board)
                if (r, c) not in opp_attacks:  # not currently in check
                    row = r
                    if not self.rook_moved[color]['K']:
                        if board[row][5] is None and board[row][6] is None \
                                and board[row][7] == color + 'R':
                            if (row, 5) not in opp_attacks and (row, 6) not in opp_attacks:
                                moves.append((row, 6, 'castleK'))
                    if not self.rook_moved[color]['Q']:
                        if board[row][1] is None and board[row][2] is None \
                                and board[row][3] is None and board[row][0] == color + 'R':
                            if (row, 3) not in opp_attacks and (row, 2) not in opp_attacks:
                                moves.append((row, 2, 'castleQ'))

        else:  # B, R, Q - sliding pieces
            dirs = BISHOP_DIRS if ptype == 'B' else ROOK_DIRS if ptype == 'R' else QUEEN_DIRS
            for dr, dc in dirs:
                nr, nc = r + dr, c + dc
                while in_bounds(nr, nc):
                    target = board[nr][nc]
                    if target is None:
                        moves.append((nr, nc, None))
                    else:
                        if target[0] != color:
                            moves.append((nr, nc, 'capture'))
                        break
                    nr += dr
                    nc += dc

        return moves

    # ------------------------------------------------------------------
    # Simulation helper - applies a move to a COPY of the board so that
    # legality (own-king-safety) can be checked without mutating state.
    # ------------------------------------------------------------------
    def _simulate(self, board, r, c, tr, tc, flag):
        new_board = [row[:] for row in board]
        piece = new_board[r][c]
        new_board[r][c] = None

        if flag == 'ep':
            new_board[tr][tc] = piece
            new_board[r][tc] = None  # captured pawn sits beside the mover
        elif flag == 'castleK':
            new_board[tr][tc] = piece
            new_board[r][5] = new_board[r][7]
            new_board[r][7] = None
        elif flag == 'castleQ':
            new_board[tr][tc] = piece
            new_board[r][3] = new_board[r][0]
            new_board[r][0] = None
        else:
            new_board[tr][tc] = piece

        if flag in ('promo', 'capture_promo'):
            new_board[tr][tc] = piece[0] + 'Q'  # queen for the purpose of the safety check

        return new_board

    # ------------------------------------------------------------------
    # Fully legal moves = pseudo-legal moves that do not leave the
    # mover's own king in check.
    # ------------------------------------------------------------------
    def legal_moves(self, r, c):
        piece = self.board[r][c]
        if not piece:
            return []
        color = piece[0]
        legal = []
        for (tr, tc, flag) in self.pseudo_legal_moves(r, c):
            temp = self._simulate(self.board, r, c, tr, tc, flag)
            if not self.is_in_check(color, temp):
                legal.append((tr, tc, flag))
        return legal

    def all_legal_moves(self, color):
        result = []
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece and piece[0] == color:
                    for m in self.legal_moves(r, c):
                        result.append((r, c, m[0], m[1], m[2]))
        return result

    def is_checkmate(self, color):
        return self.is_in_check(color) and len(self.all_legal_moves(color)) == 0

    def is_stalemate(self, color):
        return (not self.is_in_check(color)) and len(self.all_legal_moves(color)) == 0

    # ------------------------------------------------------------------
    # Apply a move to the REAL board. Returns (success: bool, info: dict)
    # ------------------------------------------------------------------
    def make_move(self, r, c, tr, tc, promotion_choice='Q'):
        if self.game_over:
            return False, {'reason': 'game_over'}

        piece = self.board[r][c]
        if not piece:
            return False, {'reason': 'empty_source'}
        color = piece[0]
        if color != self.turn:
            return False, {'reason': 'wrong_turn'}

        legal = self.legal_moves(r, c)
        match = next((m for m in legal if m[0] == tr and m[1] == tc), None)
        if match is None:
            return False, {'reason': 'illegal_move'}

        flag = match[2]
        captured = self.board[tr][tc]
        self.board[r][c] = None

        if flag == 'ep':
            captured = self.board[r][tc]
            self.board[tr][tc] = piece
            self.board[r][tc] = None
        elif flag == 'castleK':
            self.board[tr][tc] = piece
            self.board[r][5] = self.board[r][7]
            self.board[r][7] = None
            self.rook_moved[color]['K'] = True
        elif flag == 'castleQ':
            self.board[tr][tc] = piece
            self.board[r][3] = self.board[r][0]
            self.board[r][0] = None
            self.rook_moved[color]['Q'] = True
        else:
            self.board[tr][tc] = piece

        promoted_to = None
        if flag in ('promo', 'capture_promo'):
            choice = promotion_choice if promotion_choice in ('Q', 'R', 'B', 'N') else 'Q'
            self.board[tr][tc] = color + choice
            promoted_to = choice

        if piece[1] == 'K':
            self.king_moved[color] = True
        if piece[1] == 'R':
            if c == 0:
                self.rook_moved[color]['Q'] = True
            elif c == 7:
                self.rook_moved[color]['K'] = True
        if captured and captured[1] == 'R':
            opp = captured[0]
            if tc == 0:
                self.rook_moved[opp]['Q'] = True
            elif tc == 7:
                self.rook_moved[opp]['K'] = True

        self.en_passant_target = ((r + tr) // 2, c) if flag == 'double' else None

        self.turn = other(color)

        info = {
            'from': (r, c), 'to': (tr, tc), 'piece': piece, 'flag': flag,
            'captured': captured, 'promoted_to': promoted_to,
        }
        self.move_log.append(info)

        # Update status
        opp_color = self.turn
        if self.is_checkmate(opp_color):
            self.status = f"Checkmate - {'White' if color == 'w' else 'Black'} wins"
            self.game_over = True
        elif self.is_stalemate(opp_color):
            self.status = "Stalemate - draw"
            self.game_over = True
        elif self.is_in_check(opp_color):
            self.status = f"{'White' if opp_color == 'w' else 'Black'} is in check"
        else:
            self.status = f"{'White' if opp_color == 'w' else 'Black'} to move"

        return True, info

    def needs_promotion_choice(self, r, c, tr, tc):
        """Returns True if moving piece at (r,c) to (tr,tc) is a pawn move that
        requires a promotion choice (used by the GUI to decide whether to
        pop up a promotion dialog before calling make_move)."""
        piece = self.board[r][c]
        if not piece or piece[1] != 'P':
            return False
        promo_row = 0 if piece[0] == 'w' else 7
        return tr == promo_row
