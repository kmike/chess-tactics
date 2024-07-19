import chess
import pytest

from chess_tactics.mistakes import (
    hanging_piece_not_captured,
    hangs_moved_piece,
    missed_fork,
    unfavorable_exchange,
)

from .fens import EXAMPLE_00, EXAMPLE_01


def test_hangs_moved_piece():
    board = chess.Board(EXAMPLE_01)
    assert hangs_moved_piece(board, board.parse_san("Bd4"))
    assert not hangs_moved_piece(board, board.parse_san("Bb2"))

    # exchange is considered a separate mistake
    assert not hangs_moved_piece(board, board.parse_san("Bxe5"))

    # If, for some reason, capturing is not the best move for the opponent,
    # a move is no longer considered as a mistake of this type
    assert not hangs_moved_piece(
        board, board.parse_san("Bd4"), best_opponent_moves=[chess.Move.from_uci("g7g8")]
    )


def test_unfavorable_exchange():
    board = chess.Board(EXAMPLE_01)
    assert unfavorable_exchange(board, board.parse_san("Bxe5"))
    assert not unfavorable_exchange(board, board.parse_san("Bb2"))

    # hanging a piece is considered a separate mistake
    assert not unfavorable_exchange(board, board.parse_san("Bd4"))

    # If, for some reason, recapturing is not the best move for the opponent,
    # a move is no longer considered as a mistake of this type
    assert not unfavorable_exchange(
        board, board.parse_san("Be5"), best_opponent_moves=[chess.Move.from_uci("g7g8")]
    )


def test_hanging_piece_not_captured():
    board = chess.Board(EXAMPLE_00)
    best_moves = [board.parse_san("Bxe5")]

    assert hanging_piece_not_captured(board, board.parse_san("Bb2"), best_moves)


@pytest.mark.parametrize(
    ["fen", "best_moves_san", "move_san", "fork_missing"],
    [
        ("k7/8/1q3r2/8/8/4N3/2K5/8 w - - 0 1", ["Nd5"], "Nc4", True),
        ("k7/8/1q3r2/8/8/4N3/2K5/8 w - - 0 1", ["Nd5"], "Nd5", False),
        # best move is not a fork
        ("k7/8/1q3r2/8/8/4N3/2K5/8 w - - 0 1", ["Kd2"], "Nc4", False),
        # fork is found, but not the best one
        ("k7/8/1q3r2/8/8/r3N3/2K5/8 w - - 0 1", ["Nd5"], "Nc4", False),
        # multiple best moves
        ("k7/8/1q3r2/8/8/r3N3/2K5/8 w - - 0 1", ["Kd2", "Nd5"], "Ng2", True),
    ],
)
def test_missed_fork(fen, best_moves_san, move_san, fork_missing):
    board = chess.Board(fen)
    best_moves = [board.parse_san(m) for m in best_moves_san]
    move = board.parse_san(move_san)
    assert missed_fork(board, move, best_moves) is fork_missing
