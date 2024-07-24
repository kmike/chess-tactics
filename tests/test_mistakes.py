import chess
import pytest

from chess_tactics.mistakes import (
    hanging_piece_not_captured,
    hung_moved_piece,
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
