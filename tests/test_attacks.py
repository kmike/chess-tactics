import chess

from chess_tactics.attacks import get_attackers, get_least_valuable_attacker

from .fens import (
    EXAMPLE7,
    EXAMPLE8,
    EXAMPLE8_1,
    EXAMPLE9,
    ILLEGAL_KING_ATTACK,
    NIMZOVICH_TARRASCH,
)


def test_get_least_valuable_attacker():
    board = chess.Board(NIMZOVICH_TARRASCH)
    assert get_least_valuable_attacker(board, chess.BLACK, chess.F1) == chess.G2
    assert get_least_valuable_attacker(board, chess.BLACK, chess.C1) is None


class TestGetAttackers:
    def test_original(self):
        # original test from python-chess
        board = chess.Board(
            "r1b1k2r/pp1n1ppp/2p1p3/q5B1/1b1P4/P1n1PN2/1P1Q1PPP/2R1KB1R b Kkq - 3 10"
        )
        attackers = get_attackers(board, chess.WHITE, chess.C3)
        assert attackers == chess.SquareSet([chess.D2, chess.B2, chess.C1])

    def test_pinned(self):
        # pinned attackers shouldn't be included
        board = chess.Board(
            "r1b1k2r/pp1n1ppp/2p1p3/q3r1B1/1b1P4/P1n1QN2/1P3PPP/2R1KB1R b Kkq - 3 10"
        )

        attackers = get_attackers(board, chess.WHITE, chess.C3)
        orig_attackers = board.attackers(chess.WHITE, chess.C3)

        assert chess.E3 in orig_attackers
        assert chess.E3 not in attackers
        assert attackers == chess.SquareSet([chess.B2, chess.C1])

        # pinned attacker still attacks a piece which pins it
        attackers = get_attackers(board, chess.WHITE, chess.E5)
        assert attackers == chess.SquareSet([chess.E3, chess.F3, chess.D4])

        # a case with no attackers
        attackers = get_attackers(board, chess.WHITE, chess.E6)
        assert attackers == chess.SquareSet()

    def test_illegal_king_move(self):
        board = chess.Board(ILLEGAL_KING_ATTACK)
        attackers = get_attackers(board, chess.WHITE, chess.D4)
        assert attackers == chess.SquareSet()

    def test_king_in_check(self):
        # pawn can't be taken, king is in check
        board = chess.Board(EXAMPLE7)
        assert not get_attackers(board, chess.WHITE, chess.E5)

    def test_king_in_double_check_but_can_escape_by_taking(self):
        # king can take the pawn and escape
        board = chess.Board(EXAMPLE8)
        assert get_attackers(board, chess.WHITE, chess.C2) == chess.SquareSet(
            [chess.B1]
        )

    def test_double_check_only_king_can_take(self):
        # king can take the pawn and escape, but bishop can't
        board = chess.Board(EXAMPLE8_1)
        assert get_attackers(board, chess.WHITE, chess.C2) == chess.SquareSet(
            [chess.B1]
        )

    def test_checker_can_be_taken(self):
        # pawn checks the king, and king can't take it, but bishop can
        board = chess.Board(EXAMPLE9)
        assert get_attackers(board, chess.WHITE, chess.C2) == chess.SquareSet(
            [chess.E4]
        )
