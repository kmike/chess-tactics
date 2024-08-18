"""
A module with heuristics for detecting various tactical mistakes.

Engine analysis should be used to generate best moves, and to validate
if a move is actually a mistake.
"""

from typing import Optional

import chess
import chess.engine

from .exchange import (
    get_capture_exchange_evaluation,
    get_exchange_evaluation,
    get_move_captured_value,
)
from .tactics import get_hanging_pieces, is_forking_move, is_hanging


def hanging_piece_not_captured(
    board: chess.Board, move: chess.Move, best_moves: list[chess.Move]
) -> bool:
    """Return True if *move* failed to capture a hanging piece."""

    # XXX: This probably should take in account values of the exchange
    # started by the capture, to detect cases where a wrong piece was
    # captured, or a wrong piece was used to capture.
    # Or should it be considered a separate mistake?

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
        # see started_bad_trade mistake
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

    new_hanging_value = _new_hanging_after_move_value(board, move)

    # some new pieces should be hanging after the move
    if not new_hanging_value:
        return False

    # less value should be hanging in at least
    # one of the suggested variations
    if best_moves:
        hanging_after_best_move_value = min(
            _new_hanging_after_move_value(board, m) for m in best_moves
        )
        return hanging_after_best_move_value < new_hanging_value

    return True


def left_piece_hanging(
    board: chess.Board,
    move: chess.Move,
    best_moves: Optional[list[chess.Move]] = None,
) -> bool:
    """
    Return if a *move* failed to address an issue with a hanging piece:

    * there was a hanging piece on the board (e.g. because opponent just
      attacked it),
    * *move* still left it hanging, by not moving it, and not defending it.
    * the best move was not to let it hang.

    Cases where a hanging piece is moved to another square where
    it can be captured are handled by :func:`hung_moved_piece`.
    This function (:func:`left_piece_hanging`) returns False in such
    cases - the piece is not "left" hanging.
    """
    if best_moves and move in best_moves:
        return False

    # fixme: counter-attacks?
    # fixme: saving one of the pieces when more than 1 is hanging
    # is not considered enough if their value is the same
    color = board.color_at(move.from_square)
    hanging_now = get_hanging_pieces(board, color)

    # there should be some hanging pieces now
    if not hanging_now:
        return False

    # the hanging piece is moved - it's not "left" hanging;
    # even if the move hangs it again, it's going to be a separate mistake
    # ("hung_moved_piece").
    if all(move.from_square == s for s in hanging_now):
        return False

    hanging_after_move_value = _hanging_after_move_value(
        board, move
    ) - get_move_captured_value(board, move)

    if not best_moves:
        # if best_moves are not passed, assume hanging pieces can be saved
        hanging_after_best_move_value = 0
    else:
        hanging_after_best_move_value = min(
            _hanging_after_move_value(board, m) - get_move_captured_value(board, m)
            for m in best_moves
        )

        # if we fail to capture more, but still saved the hanging piece, it's
        # a separate mistake (hanging_piece_not_captured?).
        hanging_after_best_move_value = max(hanging_after_best_move_value, 0)

        # Basic logic for now. It could happen that
        # hanging_after_best_move_value >= hanging_now_value, i.e. the best
        # move is not about saving those pieces.
        # In this case, we return True only if the value hanged by the actual
        # move is even more than the hanging_after_best_move_value.

    # TODO: best opponent move should be to capture the hanging piece?
    return hanging_after_best_move_value < hanging_after_move_value


def missed_fork(
    board: chess.Board, move: chess.Move, best_moves: list[chess.Move]
) -> bool:
    """Return True if a *move* is a missed fork opportunity"""
    if is_forking_move(board, move):
        return False

    return any(is_forking_move(board, m) for m in best_moves)


def hung_fork(
    board: chess.Board,
    move: chess.Move,
    best_opponent_moves: list[chess.Move],
    pv: Optional[list[chess.Move]] = None,
) -> bool:
    """Return True if a *move* allowed opponent to make a fork"""
    if not best_opponent_moves:
        return False

    # one of the best responses for the opponent should be to fork us
    board_after = board.copy()
    board_after.push(move)
    if not any(is_forking_move(board_after, m) for m in best_opponent_moves):
        return False

    # if after the best response opponent still forks us, the move which
    # is made is not hanging a fork
    if pv and len(pv) >= 2:
        best_move, best_move_response = pv[:2]
        board_after = board.copy()
        board_after.push(best_move)
        if is_forking_move(board_after, best_move_response):
            return False

    return True


def hung_mate_n(
    pov_white_score: chess.engine.Score,
    pov_white_best_score: chess.engine.Score,
    n: int,
) -> bool:
    """Return True if the player allowed mate in *n*"""
    m = chess.engine.Mate(-n)
    return pov_white_score == m and pov_white_best_score > m


def hung_mate_n_plus(
    pov_white_score: chess.engine.Score,
    pov_white_best_score: chess.engine.Score,
    n: int,
) -> bool:
    """
    Return True if the player allowed mate in *n+*, while the best
    outcome was not to get mated at all.
    """

    def _getting_mated(score: chess.engine.Score) -> bool:
        mate = score.mate()
        return mate is not None and mate < 0

    return (
        _getting_mated(pov_white_score)
        and pov_white_score >= chess.engine.Mate(-n)
        and not _getting_mated(pov_white_best_score)
    )


def missed_mate_n(
    pov_white_score: chess.engine.Score,
    pov_white_best_score: chess.engine.Score,
    n: int,
) -> bool:
    """Return True if the player missed mate in *n*"""
    m = chess.engine.Mate(n)
    return pov_white_best_score == m and pov_white_score < m


def missed_mate_n_plus(
    pov_white_score: chess.engine.Score,
    pov_white_best_score: chess.engine.Score,
    n: int,
) -> bool:
    """Return True if the player missed mate in *n+*."""

    def _mating(score: chess.engine.Score) -> bool:
        mate = score.mate()
        return mate is not None and mate > 0

    return (
        not _mating(pov_white_score)
        and _mating(pov_white_best_score)
        and pov_white_best_score <= chess.engine.Mate(n)
    )


def missed_sacrifice(
    board: chess.Board,
    move: chess.Move,
    best_moves: list[chess.Move],
) -> bool:
    """
    Return True if one of *best_moves* is a sacrifice, while *move* isn't.
    This includes both real sacrifices and sham (pseudo) sacrifices.
    """
    if move in best_moves:
        return False

    def _is_sacrifice(b, m) -> bool:
        # the moved piece is sacrificed by capturing something
        # fixme: don't consider discovered attacks sacrifices
        if started_bad_trade(b, m):
            return True

        # Moved piece is put into hanging position. We should
        # start detecting relative pins before implementing it, because
        # otherwise many simple tactics involving pins would be considered
        # sacrifices.
        # if hung_moved_piece(b, m):
        #     return True

        # Another piece is left hanging. The issue is that in practice
        # the code below usually shows cases which don't look
        # like sacrifices (?). It needs more investigation.
        # if hung_other_piece(b, m):
        #     return True

        # The move drops protection for another piece. This also doesn't work
        # as-is, results don't look good.
        # if left_piece_hanging(b, m):
        #     return True

        return False

    return any(_is_sacrifice(board, move) for move in best_moves)


def _moved_piece_should_be_captured_because_it_hangs(
    board: chess.Board,
    move: chess.Move,
    best_opponent_moves: Optional[list[chess.Move]] = None,
) -> bool:
    # One of the best opponent moves should be to capture the moved piece.
    if best_opponent_moves:
        if not any(m.to_square == move.to_square for m in best_opponent_moves):
            return False

    # fixme: consider value of other pieces when best_opponent_moves
    # are not provided?
    return get_capture_exchange_evaluation(board, move) < 0


def _new_hanging_after_move_value(board: chess.Board, move: chess.Move) -> int:
    """Return the max value of the newly hanging pieces after the move.
    The piece which just moved doesn't count."""

    color = board.color_at(move.from_square)
    hanging_now = get_hanging_pieces(board, color) - {move.from_square}

    # the piece itself is not considered here
    board_after, hanging_after_move = _hanging_after_move(board, move)
    new_hanging_after_move = hanging_after_move - hanging_now - {move.to_square}
    return _get_hanging_value(board_after, new_hanging_after_move)


def _hanging_after_move_value(board: chess.Board, move: chess.Move) -> int:
    """Return the max value of a piece hanging after the move"""
    board_after, hanging_after_move = _hanging_after_move(board, move)
    return _get_hanging_value(board_after, hanging_after_move)


def _hanging_after_move(
    board: chess.Board,
    move: chess.Move,
) -> tuple[chess.Board, chess.SquareSet]:
    """Return the board after the move, and the pieces which
    are hanging after the move."""
    color = board.color_at(move.from_square)
    board_after = board.copy()
    board_after.push(move)
    hanging = get_hanging_pieces(board_after, color)
    return board_after, hanging


def _get_hanging_value(board: chess.Board, hanging: chess.SquareSet) -> int:
    if not hanging:
        return 0
    return max(
        get_exchange_evaluation(board, not board.color_at(s), s) for s in hanging
    )
