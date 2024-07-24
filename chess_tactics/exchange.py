""" Static Exchange Evaluation functions """

from typing import Optional

import chess

from .attacks import get_least_valuable_attacker, in_check
from .values import get_square_value


def get_exchange_evaluation(
    board: chess.Board,
    color: chess.Color,
    square: chess.Square,
    *,
    square_value_before_promotion: Optional[float] = None,
) -> int:
    """
    Simulate an exchange at ``square``, started by ``color``, and return
    the likely material value change.

    Both players try to be reasonable and avoid material loss, i.e.
    unfavorable captures shouldn't happen.

    Ulike :func:`get_capture_exchange_evaluation`, the first move is not forced.
    """
    # If opponent's king is in check, it's an impossible exchange:
    # it must be opponent's move, not ours. The function is still useful in
    # this context, but it makes "king in check" heuristics incorrect
    # (or at least I haven't yet found a way to do it properly),
    # so the logic to handle it is disabled.
    ignore_check = in_check(board, not color)

    def _get_exchange_evaluation(
        board, color, square, square_value_before_promotion=None
    ) -> int:
        value = 0
        attacker = get_least_valuable_attacker(
            board, color, square, ignore_check=ignore_check
        )
        if attacker is not None:
            board_copy = board.copy()
            # TODO: handle promotions properly
            move = chess.Move(from_square=attacker, to_square=square)
            captured_value = _get_move_capture_value(board, move)
            board_copy.push(move)
            recapture_value = _get_exchange_evaluation(board_copy, not color, square)
            if captured_value < recapture_value:
                value = 0
            else:
                if square_value_before_promotion is not None:
                    value = square_value_before_promotion - recapture_value
                else:
                    value = captured_value - recapture_value

        return value

    return _get_exchange_evaluation(
        board,
        color,
        square,
        square_value_before_promotion=square_value_before_promotion,
    )


def get_capture_exchange_evaluation(board: chess.Board, move: chess.Move) -> int:
    """
    Return the likely material value change after *move*,
    followed by an exchange.

    Unlike :func:`get_exchange_evaluation`, the first move is forced,
    so the value can be negative.
    """
    color = board.color_at(move.from_square)
    captured_value = _get_move_capture_value(board, move)
    attacker_value = get_square_value(board, move.from_square)

    board_copy = board.copy()
    board_copy.push(move)

    exchange_value = get_exchange_evaluation(
        board_copy,
        not color,
        move.to_square,
        square_value_before_promotion=attacker_value,
    )
    return captured_value - exchange_value


def _get_move_capture_value(board: chess.Board, move: chess.Move) -> int:
    if board.is_en_passant(move):
        return 1
    else:
        return get_square_value(board, move.to_square)
