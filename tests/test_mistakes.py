import chess

from chess_tactics.mistakes import (
    hanging_piece_not_captured,
    hangs_moved_piece,
    unfavorable_exchange,
)

from .fens import EXAMPLE0, EXAMPLE1


def test_hangs_moved_piece():
    board = chess.Board(EXAMPLE1)
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
    board = chess.Board(EXAMPLE1)
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
    board = chess.Board(EXAMPLE0)
    best_moves = [board.parse_san("Bxe5")]

    assert hanging_piece_not_captured(board, board.parse_san("Bb2"), best_moves)
