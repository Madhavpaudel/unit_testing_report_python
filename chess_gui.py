"""
Chess Engine - Move Validation Only
------------------------------------
Tkinter GUI on top of chess_engine.ChessEngine.

Run with:  python3 chess_gui.py

This is a two-player, click-to-move board. There is no AI opponent -
White and Black take turns on the same computer, and every move is
checked for legality by the engine (piece movement, captures, check,
checkmate, castling, en passant, and promotion).
"""

import tkinter as tk
from tkinter import messagebox
from chess_engine import ChessEngine, other

SQUARE = 64
BOARD_PX = SQUARE * 8

LIGHT = "#EDEED1"
DARK = "#779556"
SELECTED = "#F6F669"
LEGAL_DOT = "#3A3A3A"
LEGAL_CAPTURE_RING = "#C0392B"
CHECK_COLOR = "#E74C3C"
LAST_MOVE = "#BACA44"

UNICODE_PIECES = {
    'wK': '\u2654', 'wQ': '\u2655', 'wR': '\u2656',
    'wB': '\u2657', 'wN': '\u2658', 'wP': '\u2659',
    'bK': '\u265A', 'bQ': '\u265B', 'bR': '\u265C',
    'bB': '\u265D', 'bN': '\u265E', 'bP': '\u265F',
}

FILES = "abcdefgh"


def square_name(r, c):
    return f"{FILES[c]}{8 - r}"


class PromotionDialog(tk.Toplevel):
    """Modal dialog letting the player choose a promotion piece."""

    def __init__(self, parent, color):
        super().__init__(parent)
        self.title("Pawn Promotion")
        self.resizable(False, False)
        self.choice = 'Q'
        self.transient(parent)
        self.grab_set()

        tk.Label(self, text="Promote pawn to:", font=("Helvetica", 12)).pack(padx=16, pady=(12, 6))
        row = tk.Frame(self)
        row.pack(padx=16, pady=(0, 16))

        for piece_type, label in (('Q', 'Queen'), ('R', 'Rook'), ('B', 'Bishop'), ('N', 'Knight')):
            symbol = UNICODE_PIECES[color + piece_type]
            btn = tk.Button(row, text=f"{symbol}\n{label}", font=("Helvetica", 20),
                             width=4, command=lambda pt=piece_type: self._choose(pt))
            btn.pack(side=tk.LEFT, padx=4)

        self.protocol("WM_DELETE_WINDOW", lambda: self._choose('Q'))
        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")

    def _choose(self, piece_type):
        self.choice = piece_type
        self.destroy()


class ChessGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Chess Engine - Move Validation")
        self.engine = ChessEngine()

        self.selected = None          # (r, c) of currently selected piece
        self.legal_targets = {}       # (r, c) -> flag, for the selected piece
        self.last_move = None         # (from, to) for highlighting
        self.invalid_square = None    # (r, c) briefly flashed red on a rejected click

        top = tk.Frame(root)
        top.pack(padx=10, pady=(10, 0))

        self.status_var = tk.StringVar(value="White to move")
        self.status_label = tk.Label(top, textvariable=self.status_var,
                                      font=("Helvetica", 14, "bold"))
        self.status_label.pack(side=tk.LEFT)

        self.message_var = tk.StringVar(value="")
        self.message_label = tk.Label(root, textvariable=self.message_var,
                                       font=("Helvetica", 11, "italic"), fg=CHECK_COLOR)
        self.message_label.pack(padx=10, pady=(0, 4))

        self.canvas = tk.Canvas(root, width=BOARD_PX, height=BOARD_PX, highlightthickness=0)
        self.canvas.pack(padx=10, pady=10)
        self.canvas.bind("<Button-1>", self.on_click)

        bottom = tk.Frame(root)
        bottom.pack(padx=10, pady=(0, 10), fill=tk.X)

        tk.Button(bottom, text="New Game", command=self.new_game).pack(side=tk.LEFT)
        self.log_var = tk.StringVar(value="")
        tk.Label(bottom, textvariable=self.log_var, anchor="w", justify=tk.LEFT,
                 font=("Helvetica", 10)).pack(side=tk.LEFT, padx=12)

        self.draw_board()

    # ------------------------------------------------------------------
    def new_game(self):
        self.engine = ChessEngine()
        self.selected = None
        self.legal_targets = {}
        self.last_move = None
        self.log_var.set("")
        self.draw_board()

    def square_to_xy(self, r, c):
        return c * SQUARE, r * SQUARE

    def xy_to_square(self, x, y):
        return y // SQUARE, x // SQUARE

    # ------------------------------------------------------------------
    def draw_board(self):
        self.canvas.delete("all")

        in_check_square = None
        if not self.engine.game_over and self.engine.is_in_check(self.engine.turn):
            in_check_square = self.engine.find_king(self.engine.turn)

        for r in range(8):
            for c in range(8):
                x0, y0 = self.square_to_xy(r, c)
                x1, y1 = x0 + SQUARE, y0 + SQUARE
                color = LIGHT if (r + c) % 2 == 0 else DARK

                if self.last_move and (r, c) in self.last_move:
                    color = LAST_MOVE
                if self.selected == (r, c):
                    color = SELECTED

                self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="")

                if in_check_square == (r, c):
                    self.canvas.create_rectangle(x0 + 2, y0 + 2, x1 - 2, y1 - 2,
                                                  outline=CHECK_COLOR, width=4)

                if self.invalid_square == (r, c):
                    self.canvas.create_rectangle(x0 + 2, y0 + 2, x1 - 2, y1 - 2,
                                                  outline=CHECK_COLOR, width=4, dash=(4, 2))

                piece = self.engine.board[r][c]
                if piece:
                    self.canvas.create_text(x0 + SQUARE / 2, y0 + SQUARE / 2,
                                             text=UNICODE_PIECES[piece],
                                             font=("Helvetica", int(SQUARE * 0.7)))

                if (r, c) in self.legal_targets:
                    flag = self.legal_targets[(r, c)]
                    cx, cy = x0 + SQUARE / 2, y0 + SQUARE / 2
                    if flag in ('capture', 'capture_promo', 'ep'):
                        self.canvas.create_oval(x0 + 4, y0 + 4, x1 - 4, y1 - 4,
                                                 outline=LEGAL_CAPTURE_RING, width=4)
                    else:
                        rad = SQUARE * 0.14
                        self.canvas.create_oval(cx - rad, cy - rad, cx + rad, cy + rad,
                                                 fill=LEGAL_DOT, outline="")

        # File / rank labels
        for c in range(8):
            self.canvas.create_text(c * SQUARE + 6, BOARD_PX - 8, text=FILES[c],
                                     font=("Helvetica", 8),
                                     fill=DARK if c % 2 == 0 else LIGHT, anchor="sw")
        for r in range(8):
            self.canvas.create_text(BOARD_PX - 6, r * SQUARE + 8, text=str(8 - r),
                                     font=("Helvetica", 8),
                                     fill=DARK if r % 2 == 0 else LIGHT, anchor="ne")

        self.status_var.set(self.engine.status)

    # ------------------------------------------------------------------
    def player_label(self, color):
        return "Player 1 (White)" if color == 'w' else "Player 2 (Black)"

    # ------------------------------------------------------------------
    def on_click(self, event):
        if self.engine.game_over:
            print(f"GAME OVER: {self.engine.status}. No further moves are allowed - "
                  f"click 'New Game' to start again.")
            self.message_var.set(f"Game over - {self.engine.status}. Click 'New Game' to play again.")
            return
        r, c = self.xy_to_square(event.x, event.y)
        if not (0 <= r < 8 and 0 <= c < 8):
            return

        piece = self.engine.board[r][c]

        if self.selected is None:
            if piece and piece[0] == self.engine.turn:
                self.select_square(r, c)
            elif piece:
                self.reject(f"It's {('White' if self.engine.turn == 'w' else 'Black')}'s "
                             f"turn - you clicked {square_name(r, c)}, an opponent piece.")
            return

        if (r, c) == self.selected:
            self.clear_selection()
            return

        if (r, c) in self.legal_targets:
            self.attempt_move(self.selected, (r, c))
            return

        if piece and piece[0] == self.engine.turn:
            self.select_square(r, c)
            return

        # Clicked a square that is not a legal destination for the
        # currently selected piece - reject it with feedback instead of
        # silently deselecting.
        src_name = square_name(*self.selected)
        dst_name = square_name(r, c)
        self.reject(f"Illegal move: {src_name} to {dst_name} is not allowed for that piece.")
        self.flash_invalid_square(r, c)

    def reject(self, message):
        """Report an illegal move attempt both to the console (for your
        test-evidence screenshots) and on screen."""
        print(f"REJECTED: {message}")
        self.message_var.set(message)
        # Revert to the normal status line after a short delay so the
        # rejection message doesn't linger forever.
        self.root.after(2000, lambda: self.message_var.set(""))

    def flash_invalid_square(self, r, c):
        """Briefly outline the rejected destination square in red."""
        self.invalid_square = (r, c)
        self.draw_board()
        self.root.after(400, self.clear_invalid_flash)

    def clear_invalid_flash(self):
        self.invalid_square = None
        self.draw_board()

    def select_square(self, r, c):
        self.selected = (r, c)
        moves = self.engine.legal_moves(r, c)
        self.legal_targets = {(tr, tc): flag for (tr, tc, flag) in moves}
        self.draw_board()

    def clear_selection(self):
        self.selected = None
        self.legal_targets = {}
        self.draw_board()

    def attempt_move(self, src, dst):
        r, c = src
        tr, tc = dst
        promotion_choice = 'Q'
        if self.engine.needs_promotion_choice(r, c, tr, tc):
            color = self.engine.board[r][c][0]
            dialog = PromotionDialog(self.root, color)
            self.root.wait_window(dialog)
            promotion_choice = dialog.choice

        ok, info = self.engine.make_move(r, c, tr, tc, promotion_choice=promotion_choice)
        if not ok:
            # Should be rare, since on_click only offers pre-filtered legal
            # targets - but kept as a safety net so the engine's own
            # rejection is never silently swallowed.
            self.reject(f"Illegal move rejected by engine: "
                         f"{square_name(r, c)} to {square_name(tr, tc)} "
                         f"({info.get('reason', 'unknown reason')}).")
            self.clear_selection()
            return

        self.last_move = (src, dst)
        self.selected = None
        self.legal_targets = {}
        self.log_move(info)
        self.announce_result(info)
        self.draw_board()

        if self.engine.game_over:
            self.root.after(150, lambda: messagebox.showinfo("Game Over", self.engine.status))

    def announce_result(self, info):
        """Print a clear, plain-English console message for every
        significant outcome of a move: the move itself, a check alert,
        or a checkmate / stalemate result with the winner announced."""
        mover_color = info['piece'][0]
        opponent_color = other(mover_color)

        src_name = square_name(*info['from'])
        dst_name = square_name(*info['to'])
        extra = ""
        if info['flag'] == 'ep':
            extra = " (en passant)"
        elif info['flag'] in ('castleK', 'castleQ'):
            extra = " (castling)"
        elif info['promoted_to']:
            extra = f" (promotes to {info['promoted_to']})"
        elif info['captured']:
            extra = " (capture)"
        print(f"MOVE: {self.player_label(mover_color)} played "
              f"{info['piece'][1]} {src_name} to {dst_name}{extra}.")

        if self.engine.is_checkmate(opponent_color):
            print(f"CHECKMATE! {self.player_label(opponent_color)}'s king "
                  f"({'White' if opponent_color == 'w' else 'Black'}) has no legal move left "
                  f"to escape check - every possible square is either occupied by a friendly "
                  f"piece, still attacked, or blocked.")
            print(f"RESULT: {self.player_label(mover_color)} wins the game.")
        elif self.engine.is_stalemate(opponent_color):
            print(f"STALEMATE: {self.player_label(opponent_color)}'s king is NOT in check, "
                  f"but has no legal move available - no side wins.")
            print("RESULT: Draw.")
        elif self.engine.is_in_check(opponent_color):
            print(f"CHECK! {self.player_label(opponent_color)}'s king "
                  f"({'White' if opponent_color == 'w' else 'Black'}) is under attack and "
                  f"must move out of check, block the attack, or capture the attacker.")

    def log_move(self, info):
        piece_symbol = info['piece'][1]
        src_name = square_name(*info['from'])
        dst_name = square_name(*info['to'])
        note = ""
        if info['flag'] == 'castleK':
            note = " (kingside castling)"
        elif info['flag'] == 'castleQ':
            note = " (queenside castling)"
        elif info['flag'] == 'ep':
            note = " (en passant)"
        elif info['promoted_to']:
            note = f" (promotes to {info['promoted_to']})"
        elif info['captured']:
            note = " (capture)"
        self.log_var.set(f"Last move: {piece_symbol}{src_name}-{dst_name}{note}")


def main():
    root = tk.Tk()
    ChessGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
