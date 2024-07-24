"""
A module with heuristics for detecting various tactical mistakes.

Engine analysis should be used to generate best moves, and to validate
if a move is actually a mistake.
"""

from typing import Optional

import chess

from .exchange import get_capture_exchange_evaluation
from .tactics import (
    get_hanging_pieces,
    is_forking_move,
    is_hanging,
)


def hanging_piece_not_captured(
    board: chess.Board, move: chess.Move, best_moves: list[chess.Move]
) -> bool:
    """Return True if *move* failed to capture a hanging piece."""

    # XXX: This probably should take in account values of the exchange
    # started by the capture, to detect cases where a wrong piece was
    # captured. Or should it be considered a separate mistake?

    # The move which is made shouldn't be a capture of a hanging piece (??).
    if is_hanging(board, move.to_square):
        return False

    # One of best_moves should be a capture of a hanging piece.
    return any(is_hanging(board, m.to_square) for m in best_moves)


def hung_moved_piece(
    board: chess.Board,
    move: chess.Move,
    best_opponent_moves: Optional[list[chess.Move]] = None,
) -> bool:
    """Return True if *move* hangs a piece."""
    if board.is_capture(move):
        # see started_best_trade mistake
        return False

    return _moved_piece_should_be_captured_because_it_hangs(
        board, move, best_opponent_moves
    )


def started_bad_trade(
    board: chess.Board,
    move: chess.Move,
    best_opponent_moves: Optional[list[chess.Move]] = None,
) -> bool:
    """Return True if *move* is a capture which starts an unfavorable exchange,
    i.e. a trade which loses material."""
    if not board.is_capture(move):
        # see hung_moved_piece mistake
        return False

    return _moved_piece_should_be_captured_because_it_hangs(
        board, move, best_opponent_moves
    )


def hung_other_piece(
    board: chess.Board,
    move: chess.Move,
    best_moves: Optional[list[chess.Move]] = None,
) -> bool:
    """Return True if *move* made one of the other pieces hang:

    * either by stopping to defend it,
    * or by exposing it to an attack,
    * or by removing a pin on the attacker,
    * or because of other tactical reasons.
    """
    # XXX: should it handle counter-attacks, captures? I.e. a defence
    # is removed, but a piece of a higher value is attacked
    # (or maybe captured, which is a separate case)?

    new_hanging_value = _new_hanging_value(board, move)

    # some new pieces should be hanging after the move
    if not new_hanging_value:
        return False

    # less value should be hanging in at least
    # one of the suggested variations
    if best_moves:
        hanging_after_best_move_value = min(
            _new_hanging_value(board, m)
            for m in best_moves
        )
        return hanging_after_best_move_value < new_hanging_value

    return True


def _new_hanging_value(board: chess.Board, move: chess.Move) -> int:
    board_after = board.copy()
    board_after.push(move)
    color = board.color_at(move.from_square)

    hanging_now = get_hanging_pieces(board, color)
    hanging_after_move = get_hanging_pieces(board_after, color)
    new_hanging_after_move = hanging_after_move - hanging_now
    other_new_hanging_after_move = new_hanging_after_move - {move.to_square}
    return _get_hanging_value(board_after, other_new_hanging_after_move)


def _get_hanging_value(board: chess.Board, hanging: chess.SquareSet) -> int:
    if not hanging:
        return 0
    return max(get_exchange_evaluation(board, not board.color_at(s), s) for s in hanging)


def missed_fork(
    board: chess.Board, move: chess.Move, best_moves: list[chess.Move]
) -> bool:
    """Return True if a *move* is a missed fork opportunity"""
    if is_forking_move(board, move):
        return False

    return any(is_forking_move(board, m) for m in best_moves)


def _moved_piece_should_be_captured_because_it_hangs(
    board: chess.Board,
    move: chess.Move,
    best_opponent_moves: Optional[list[chess.Move]] = None,
) -> bool:
    # One of the best opponent moves should be to capture the moved piece.
    if best_opponent_moves:
        if not any(m.to_square == move.to_square for m in best_opponent_moves):
            return False

    return get_capture_exchange_evaluation(board, move) < 0
