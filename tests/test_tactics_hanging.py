import chess
import pytest

from chess_tactics.tactics import get_hanging_pieces, is_hanging

from .fens import (
    EXAMPLE0,
    EXAMPLE1,
    EXAMPLE2,
    EXAMPLE3,
    EXAMPLE4,
    EXAMPLE5,
    EXAMPLE6,
    EXAMPLE7,
    EXAMPLE8,
    EXAMPLE8_1,
    EXAMPLE9,
    ILLEGAL_KING_ATTACK,
    NIMZOVICH_TARRASCH,
)


class TestHanging:
    @pytest.mark.parametrize(
        ["fen", "expected"],
        [
            (EXAMPLE0, True),
            (EXAMPLE1, False),
            (EXAMPLE2, True),
            (EXAMPLE3, False),
            (EXAMPLE4, True),
            (EXAMPLE5, False),
        ],
    )
    def test_basic_examples(self, fen, expected):
        board = chess.Board(fen)
        assert is_hanging(board, chess.E5) is expected

        pieces = get_hanging_pieces(board, chess.BLACK)
        if expected:
            assert pieces == chess.SquareSet([chess.E5])
        else:
            assert pieces == chess.SquareSet([])

    def test_pinned_attacker(self):
        board = chess.Board(EXAMPLE6)

        # pinned Q doesn't count as an attacker for E5
        assert not is_hanging(board, chess.E5)

        # but it counts as an attacker for the piece which pins is
        assert is_hanging(board, chess.B7)

        # nothing else is hanging
        hanging = get_hanging_pieces(board, chess.BLACK)
        assert hanging == chess.SquareSet([chess.B7])

    def test_illegal_king_move(self):
        board = chess.Board(ILLEGAL_KING_ATTACK)
        assert not is_hanging(board, chess.D4)
        assert not get_hanging_pieces(board, chess.BLACK)

    def test_get_hanging_pieces(self):
        board = chess.Board(NIMZOVICH_TARRASCH)
        hanging = get_hanging_pieces(board, chess.WHITE)
        assert hanging == chess.SquareSet([chess.D4, chess.F1, chess.F3])

        hanging = get_hanging_pieces(board, chess.BLACK)
        assert hanging == chess.SquareSet([chess.H1, chess.C5])

    def test_is_hanging_empty(self):
        board = chess.Board()
        assert not is_hanging(board, chess.E4)

    def test_king_in_check(self):
        # pawn can't be taken, king is in check
        board = chess.Board(EXAMPLE7)
        assert not is_hanging(board, chess.E5)
        assert get_hanging_pieces(board, chess.BLACK) == chess.SquareSet()

    def test_king_in_double_check_but_can_escape_by_taking(self):
        # king can take the pawn and escape
        for example in [EXAMPLE8, EXAMPLE8_1]:
            board = chess.Board(example)
            assert is_hanging(board, chess.C2)
            assert get_hanging_pieces(board, chess.BLACK) == chess.SquareSet([chess.C2])

    def test_checker_can_be_taken(self):
        # pawn checks the king, and king can't take it, but bishop can
        board = chess.Board(EXAMPLE9)
        assert is_hanging(board, chess.C2)
        assert get_hanging_pieces(board, chess.BLACK) == chess.SquareSet([chess.C2])
