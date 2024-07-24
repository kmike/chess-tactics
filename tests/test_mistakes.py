import chess
import pytest

from chess_tactics.mistakes import (
    hanging_piece_not_captured,
    hung_moved_piece,
    hung_other_piece,
    missed_fork,
    started_bad_trade,
)

from .fens import EXAMPLE_00, EXAMPLE_01


@pytest.mark.parametrize(
    ["fen", "move_san", "best_opponent_moves_san", "expected"],
    [
        # basic cases
        (EXAMPLE_01, "Bd4", [], True),
        (EXAMPLE_01, "Bb2", [], False),
        # bad trade is a sepatate mistake
        (EXAMPLE_01, "Bxe5", [], False),
        # If, for some reason, capturing is not the best move for the opponent,
        # a move is no longer considered as a mistake of this type
        (EXAMPLE_01, "Bd4", ["e4"], False),
    ],
)
def test_hung_moved_piece(fen, move_san, best_opponent_moves_san, expected):
    board, move, best_opponent_moves = _board_move_best_moves(fen, move_san, [])
    best_opponent_moves = _best_opponent_moves(board, move, best_opponent_moves_san)
    assert hung_moved_piece(board, move, best_opponent_moves) is expected


@pytest.mark.parametrize(["fen", "move_san", "best_opponent_moves_san", "expected"], [
    # basic cases
    (EXAMPLE_01, "Bxe5", [], True),
    (EXAMPLE_01, "Bb2", [], False),

    # hanging a piece without a capture is considered a separate mistake
    (EXAMPLE_01, "Bd4", [], False),

    # If, for some reason, recapturing is not the best move for the opponent,
    # a move is no longer considered as a mistake of this type
    (EXAMPLE_01, "Bxe5", ["Kb7"], False),
])
def test_started_bad_trade(fen, move_san, best_opponent_moves_san, expected):
    board, move, best_opponent_moves = _board_move_best_moves(
        fen, move_san, [])
    best_opponent_moves = _best_opponent_moves(board, move, best_opponent_moves_san)
    assert started_bad_trade(board, move, best_opponent_moves) is expected



def test_hanging_piece_not_captured():
    board = chess.Board(EXAMPLE_00)
    best_moves = [board.parse_san("Bxe5")]

    assert hanging_piece_not_captured(board, board.parse_san("Bb2"), best_moves)


@pytest.mark.parametrize(
    ["fen", "move_san", "best_moves_san", "expected"],
    [
        # Dropped defence
        (
            "3qr1k1/4bpp1/5n1p/r1p5/2Q5/4BN2/P4PPP/R3R1K1 b - - 1 22",
            "Kh8",
            ["Bf8"],
            True,
        ),
        # Dropped defence, but the best move also drops the defence for some reason
        (
            "3qr1k1/4bpp1/5n1p/r1p5/2Q5/4BN2/P4PPP/R3R1K1 b - - 1 22",
            "Kh8",
            ["Kh7"],
            False,
        ),
        # Dropped defence with a capture
        (
            "r2qk1nr/ppp1ppbp/2np2p1/8/2PPP3/2N1Bb2/PP3PPP/R2QKB1R w KQkq - 0 7",
            "Qxf3",
            ["gxf3"],
            True,
        ),
        # Defence is not dropped
        (
            "r2qk1nr/ppp1ppbp/2np2p1/8/2PPP3/2N1Bb2/PPN2PPP/R2QKB1R w KQkq - 0 7",
            "Qxf3",
            ["gxf3"],
            False,
        ),
        # Defence is dropped because of a pin
        (
            "2r2rk1/p2n1pp1/b3pn1p/q7/P1PP4/3Q1PB1/4B1PP/2R1K2R w K - 1 21",
            "Rc3",
            ["Qd2"],
            True,
        ),
        # Defence is dropped (c4), but the best move also drops the defence (a3)
        (
            "2r2rk1/p2n1pp1/b3pn1p/q7/2PP4/P2Q1PB1/4B1PP/2R1K2R w K - 1 21",
            "Rc3",
            ["Qd2"],
            False,
        ),
        # Block is removed
        (
            "rnbqk1nr/ppppppbp/6p1/8/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 0 1",
            "b3",
            ["d4"],
            True,
        ),
        # Pin on the attacker is removed
        (
            "r1bqkbnr/pp3ppp/2n1p3/1BppP3/3P4/2P2Q2/PP3PPP/RNB1K1NR w KQkq - 0 1",
            "Bd3",
            ["Ne2"],
            True,
        ),
        # Best move hangs less value than the move which is made (pawn vs bishop)
        (
            "r4b1r/pp1k1pp1/3p2bp/2pP4/1q2NB2/5N1P/PP2QPP1/R4RK1 w - - 3 15",
            "Nc3",
            ["Nfd2"],
            True
        )
    ],
)
def test_hung_other_piece(fen, move_san, best_moves_san, expected):
    board, move, best_moves = _board_move_best_moves(fen, move_san, best_moves_san)
    assert hung_other_piece(board, move, best_moves) is expected


@pytest.mark.parametrize(
    ["fen", "move_san", "best_moves_san", "fork_missing"],
    [
        ("k7/8/1q3r2/8/8/4N3/2K5/8 w - - 0 1", "Nc4", ["Nd5"], True),
        ("k7/8/1q3r2/8/8/4N3/2K5/8 w - - 0 1", "Nd5", ["Nd5"], False),
        # best move is not a fork
        ("k7/8/1q3r2/8/8/4N3/2K5/8 w - - 0 1", "Nc4", ["Kd2"], False),
        # fork is found, but not the best one
        ("k7/8/1q3r2/8/8/r3N3/2K5/8 w - - 0 1", "Nc4", ["Nd5"], False),
        # multiple best moves
        ("k7/8/1q3r2/8/8/r3N3/2K5/8 w - - 0 1", "Ng2", ["Kd2", "Nd5"], True),
    ],
)
def test_missed_fork(fen, move_san, best_moves_san, fork_missing):
    board, move, best_moves = _board_move_best_moves(fen, move_san, best_moves_san)
    assert missed_fork(board, move, best_moves) is fork_missing


def _board_move_best_moves(
    fen: str, move_san: str, best_moves_san: list[str]
) -> tuple[chess.Board, chess.Move, list[chess.Move]]:
    board = chess.Board(fen)
    move = board.parse_san(move_san)
    best_moves = [board.parse_san(m) for m in best_moves_san]
    return board, move, best_moves


def _best_opponent_moves(
    board: chess.Board, move: chess.Move, best_opponent_moves_san: list[str]
) -> list[chess.Move]:
    board_after_move = board.copy()
    board_after_move.push(move)
    return [board_after_move.parse_san(m) for m in best_opponent_moves_san]
