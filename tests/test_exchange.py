import chess
import pytest

from chess_tactics.exchange import (
    _greedy_exchange,
    _times_to_capture,
    get_exchange_value,
    push_exchange,
)

from .fens import (
    EXAMPLE0,
    EXAMPLE1,
    EXAMPLE2,
    EXAMPLE3,
    EXAMPLE4,
    EXAMPLE5,
    NIMZOVICH_TARRASCH,
)


@pytest.mark.parametrize(
    ["fen", "move", "expected_value"],
    [
        (EXAMPLE0, "Bxe5", 1),  # pawn capture
        (EXAMPLE0, "Bd4", -3),  # hang a bishop
        (EXAMPLE1, "Bxe5", -2),  # B for a P
        (EXAMPLE2, "Bxe5", 1),
        (EXAMPLE3, "Bxe5", -2),
        (EXAMPLE4, "Bxe5", 1),
        (EXAMPLE4, "Rxe5", 1),
        (EXAMPLE5, "Bxe5", -2),
        (EXAMPLE5, "Rxe5", -2),
        (NIMZOVICH_TARRASCH, "Bxf1", 2),
        (NIMZOVICH_TARRASCH, "Qxf1", -2),
    ],
)
def test_get_exchange_value(fen, move, expected_value):
    board = chess.Board(fen)
    if isinstance(move, str):
        move = board.parse_san(move)
    assert get_exchange_value(board, move) == expected_value


def test_greedy_exchange():
    board = chess.Board("1k2r3/5n2/8/4p3/3P4/8/4R3/4R1K1 w - - 0 1")
    moves, captured_piece_values = _greedy_exchange(board, chess.WHITE, chess.E5)

    assert captured_piece_values == [1, -1, 3, -5, 5]
    assert moves == [
        chess.Move.from_uci("d4e5"),
        chess.Move.from_uci("f7e5"),
        chess.Move.from_uci("e2e5"),
        chess.Move.from_uci("e8e5"),
        chess.Move.from_uci("e1e5"),
    ]


def test_push_exchange():
    board = chess.Board(NIMZOVICH_TARRASCH)
    old_length = len(board.move_stack)
    value = push_exchange(board, chess.BLACK, chess.F1)
    assert len(board.move_stack) == old_length + 2
    assert board.move_stack[-2:] == [
        chess.Move.from_uci("g2f1"),
        chess.Move.from_uci("c1f1"),
    ]
    assert value == 2
    assert board.fen() == "3rr1k1/p4p1p/6p1/2p5/3PN3/1P3P2/PBQ2K2/5R1q b - - 0 25"


def test_push_exchange_no_trades():
    board = chess.Board(NIMZOVICH_TARRASCH)
    board_copy = board.copy()
    value = push_exchange(board_copy, chess.BLACK, chess.E4)
    assert value == 0
    assert board_copy == board


class TestTimesToCapture:
    def test_win_simple(self):
        # A simple capture
        assert _times_to_capture([1]) == 1

    def test_win_exchange(self):
        # A pawn captures a knight, and then gets recaptured
        assert _times_to_capture([3, -1]) == 2

    def test_win_exchange_long(self):
        # Winning material in a series of captures.
        # Defender doesn't have to trade.
        assert _times_to_capture([1, -5, 5]) == 1

    def test_losing_exchange(self):
        # When a captured piece is of a less value than the attacker,
        # and attacker is recaptured, we shouldn't do exchange:
        assert _times_to_capture([1, -9]) == 0

    def test_equal_exchange(self):
        assert _times_to_capture([1, -1]) == 0

    def test_rook_for_two_pieces(self):
        # R for K+B
        assert _times_to_capture([3, -5, 3]) == 3

    def test_losing_exchange_long(self):
        # A pawn is attacked by 2 rooks and protected by 2 rooks
        assert _times_to_capture([1, -5, 5, -5]) == 0

    def test_losing_exchange_long2(self):
        # A pawn is attacked by a rook and a knight, and protected
        # by a queen and a rook.
        assert _times_to_capture([1, -3, 5, -5]) == 0

    def test_complex_win(self):
        # A pawn is attacked by a rook and a knight, and protected
        # by a queen and a rook, but the queen can only capture before the rook.
        # So, defender won't recapture.
        assert _times_to_capture([1, -3, 9, -5]) == 1

    def test_defender_doesnt_have_to_capture(self):
        # To capture: P
        # Attackers, in order: Q, R, R
        # Defenders, in order: R, Q
        # Defending queen doesn't have to capture, so this loses Q for P.
        assert _times_to_capture([1, -9, 5, -5, 9]) == 0

    def test_attacker_doesnt_have_to_capture(self):
        # To capture: R.
        # Attackers, in order: P, Q
        # Defenders, in order: K, K
        # No need to sac the queen for a knight, but the first capture is good.
        assert _times_to_capture([5, -1, 3, -9]) == 2

    def test_attacker_doesnt_have_to_capture2(self):
        # To capture: Q.
        # Attackers, in order: R, R
        # Defenders, in order: P, P
        # No need to sac the second rook for a knight.
        assert _times_to_capture([9, -5, 3, -5]) == 2
