from typing import Optional

import chess

from .values import get_square_value


def get_attackers(
    board: chess.Board,
    color: chess.Color,
    square: chess.Square,
    *,
    ignore_check: bool = False,
) -> chess.SquareSet:
    """Return a SquareSet of attackers.

    The capture should be a legal move for the attacker. So,

    * absolute pinned pieces are not included;
    * illegal king moves are not included;
    * (optional) attackers which can't move due to their king being checked
      are not included;
    """
    in_check, target_is_the_only_checker = False, False
    if not ignore_check:
        attacker_king = board.king(color)
        if attacker_king is not None:
            attacker_king_checkers = board.attackers(not color, attacker_king)
            in_check = len(attacker_king_checkers) > 0
            target_is_the_only_checker = attacker_king_checkers == chess.SquareSet(
                [square]
            )

    attackers = chess.SquareSet()
    for attacker in board.attackers(color, square):

        if board.piece_type_at(attacker) == chess.KING:
            # king can't capture if there are defenders
            if board.attackers(not color, square):
                continue
        else:
            # absolute pinned piece, and the target is not a piece
            # which pinned it
            if square not in board.pin(color, attacker):
                continue

            if not ignore_check:
                # attacking king is in check, and check can't be avoided
                # by capturing the target
                if in_check and not target_is_the_only_checker:
                    continue

        attackers.add(attacker)
    return attackers


def get_least_valuable_attacker(
    board: chess.Board,
    color: chess.Color,
    square: chess.Square,
    *,
    ignore_check: bool = False,
) -> Optional[chess.Square]:
    """Return the least valuable attacker of *square*."""
    attackers = get_attackers(board, color, square, ignore_check=ignore_check)
    if not attackers:
        return None

    return min(attackers, key=lambda a: get_square_value(board, a))


def in_check(board: chess.Board, color: chess.Color) -> bool:
    """Return True if the *color* king is in check."""
    king = board.king(color)
    if king is None:
        return False
    return board.attackers_mask(not color, king) != chess.BB_EMPTY
