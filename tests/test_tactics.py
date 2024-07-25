import chess
import pytest

from chess_tactics.tactics import (
    can_be_captured,
    get_hanging_pieces,
    is_fork,
    is_forking_move,
    is_hanging,
)

from .fens import (
    CAPTURE_WITH_PROMOTION,
    EXAMPLE_00,
    EXAMPLE_01,
    EXAMPLE_02,
    EXAMPLE_03,
    EXAMPLE_04,
    EXAMPLE_05,
    EXAMPLE_06,
    EXAMPLE_07,
    EXAMPLE_08,
    EXAMPLE_08_1,
    EXAMPLE_09,
    EXAMPLE_10,
    EXAMPLE_11,
    EXAMPLE_12,
    EXAMPLE_13,
    EXAMPLE_14,
    FORK_01,
    FORK_02,
    FORK_03,
    FORK_04,
    FORK_05,
    FORK_06,
    FORK_07,
    FORK_08,
    FORK_09,
    FORK_10,
    FORK_11,
    FORK_12,
    FORK_13,
    FORK_14,
    ILLEGAL_KING_ATTACK,
    NIMZOVICH_TARRASCH,
)


class TestHanging:
    @pytest.mark.parametrize(
        ["fen", "expected"],
        [
            (EXAMPLE_00, True),
            (EXAMPLE_01, False),
            (EXAMPLE_02, True),
            (EXAMPLE_03, False),
            (EXAMPLE_04, True),
            (EXAMPLE_05, False),
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
        board = chess.Board(EXAMPLE_06)

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
        board = chess.Board(EXAMPLE_07)
        assert not is_hanging(board, chess.E5)
        assert get_hanging_pieces(board, chess.BLACK) == chess.SquareSet()

    def test_king_in_double_check_but_can_escape_by_taking(self):
        # king can take the pawn and escape
        for example in [EXAMPLE_08, EXAMPLE_08_1]:
            board = chess.Board(example)
            assert is_hanging(board, chess.C2)
            assert get_hanging_pieces(board, chess.BLACK) == chess.SquareSet([chess.C2])

    def test_checker_can_be_taken(self):
        # pawn checks the king, and king can't take it, but bishop can
        board = chess.Board(EXAMPLE_09)
        assert is_hanging(board, chess.C2)
        assert get_hanging_pieces(board, chess.BLACK) == chess.SquareSet([chess.C2])

    def test_king_in_check_but_pawn_is_protected(self):
        board = chess.Board(FORK_12)
        assert not is_hanging(board, chess.E6)

    def test_promotion(self):
        board = chess.Board(CAPTURE_WITH_PROMOTION)
        assert is_hanging(board, chess.E8)


class TestCanBeCaptured:
    @pytest.mark.parametrize(
        ["fen", "expected"],
        [
            (EXAMPLE_10, True),
            (EXAMPLE_11, True),
            (EXAMPLE_12, False),
            (EXAMPLE_13, False),
            (EXAMPLE_14, True),
        ],
    )
    def test_basic_examples(self, fen, expected):
        board = chess.Board(fen)
        assert can_be_captured(board, chess.F6) is expected

    def test_checked_king_and_protected_pawn(self):
        board = chess.Board(FORK_12)
        assert not can_be_captured(board, chess.E6)

    def test_checked_king_and_protected_pawn2(self):
        board = chess.Board(FORK_13)
        assert not can_be_captured(board, chess.E4)

    def test_checked_king_and_protected_pawn3(self):
        board = chess.Board(FORK_14)
        assert can_be_captured(board, chess.C6)
        assert can_be_captured(board, chess.B7)
        assert not can_be_captured(board, chess.E4)

    def test_own_king_checked(self):
        board = chess.Board(EXAMPLE_07)
        assert not can_be_captured(board, chess.E5)


class TestIsFork:
    def test_basic(self):
        board = chess.Board(FORK_01)
        assert is_fork(board, chess.D5)

        # regular attack, not a fork
        board = chess.Board(EXAMPLE_00)
        assert not is_fork(board, chess.C3)

    def test_attacker_hanging(self):
        board = chess.Board(FORK_02)
        assert not is_fork(board, chess.D5)

        board = chess.Board(FORK_03)
        assert not is_fork(board, chess.D5)

    def test_attacker_protected(self):
        # can be taken only with material loss
        board = chess.Board(FORK_04)
        assert is_fork(board, chess.D5)

        # equal trade
        board = chess.Board(FORK_05)
        assert not is_fork(board, chess.D5)

    def test_pinned(self):
        # Q is pinned
        board = chess.Board(FORK_06)
        assert is_fork(board, chess.D4)

        # Q is not pinned and can capture the attacking rook
        board = chess.Board(FORK_07)
        assert not is_fork(board, chess.D4)

        # Q is pinned, but N is protected
        board = chess.Board(FORK_08)
        assert not is_fork(board, chess.D4)

    def test_protected(self):
        # protected Q and R
        board = chess.Board(FORK_09)
        assert is_fork(board, chess.E4)

        # protected Q and B
        board = chess.Board(FORK_10)
        assert not is_fork(board, chess.E4)

    def test_winning_exchange(self):
        # protected Q and B, but B exchange is winning
        board = chess.Board(FORK_11)
        assert is_fork(board, chess.E4)

    def test_king_and_protected_pawn(self):
        board = chess.Board(FORK_12)
        assert not is_fork(board, chess.D7)

    def test_king_and_protected_pawn2(self):
        board = chess.Board(FORK_13)
        assert not is_fork(board, chess.D7)


@pytest.mark.parametrize(
    ["fen", "move", "expected"],
    [
        # basic cases
        ("k7/8/1q3r2/8/8/4N3/2K5/8 w - - 0 1", "Nd5", True),
        ("k7/2r5/1q3r2/8/8/4N3/K7/8 w - - 0 1", "Nd5", True),
        ("k7/8/1q3r2/8/8/4N3/2K5/8 w - - 0 1", "Nc4", False),
        # N is hanging
        ("k7/3r4/1q3r2/8/8/4N3/2K5/8 w - - 0 1", "Nd5", False),
        ("k7/4n3/1q6/8/8/4N3/2K5/8 w - - 0 1", "Nd5", False),
        # N is protected
        ("k7/3r4/1q3r2/8/4P3/4N3/2K5/8 w - - 0 1", "Nd5", True),
        # N can be exchanged
        ("k7/1b6/1q3r2/8/4P3/4N3/2K5/8 w - - 0 1", "Nd5", False),
        # Forking a pinned piece
        ("8/8/2k5/1n4n1/B7/8/4R3/2K5 w - - 0 1", "Re5", True),
        ("8/8/2k4p/1n4n1/B7/8/4R3/2K5 w - - 0 1", "Re5", False),
        # Attacking somewhat defended pieces
        ("1k6/6p1/1p3r2/2q5/8/6N1/8/1K6 w - - 0 1", "Ne4", True),
        ("1k6/6p1/1p3b2/2q5/8/6N1/8/1K6 w - - 0 1", "Ne4", False),
        ("1k6/6p1/1p3b2/2q5/8/6N1/8/1K3R2 w - - 0 1", "Ne4", True),
        # King is involved
        ("4k3/3n1p2/4p3/1B6/Q7/8/8/4K3 w - - 2 14", "Bxd7", False),
        ("4k3/8/2n5/5p2/B3p3/8/2Q5/4K3 w - - 2 14", "Bxc6", False),
        ("4k3/1p6/2n5/5p2/B3p3/8/2Q5/4K3 w - - 2 14", "Bxc6", False),
        ("4k3/1r6/2n5/5p2/B3p3/8/2Q5/4K3 w - - 2 14", "Bxc6", True),
        ("8/1r1k4/2n5/5p2/B3p3/8/8/4K3 w HAha - 2 14", "Bxc6", False),
        # Pieces were already hanging before the move
        ("k7/8/1q3r2/8/8/2B1N3/2K5/8 w - - 0 1", "Nd5", False),
        ("k7/2r5/1q3r2/8/8/2B1N3/2K5/8 w - - 0 1", "Nd5", True),
        ("k7/8/1q3r2/8/8/4N1r1/2K5/4B3 w - - 0 1", "Nd5", True),
        # King fork
        ("k7/8/8/8/8/1nb5/8/2K5 w - - 0 1", "Kc2", True),
        # Blocking a check with a pseudo-fork
        ("7k/1r6/3p4/8/1K1b4/N7/8/8 w - - 0 1", "Nb5", False),
    ],
)
def test_is_forking_move(fen, move, expected):
    board = chess.Board(fen)
    move = board.parse_san(move)
    assert is_forking_move(board, move) is expected
