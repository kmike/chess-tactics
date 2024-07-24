import chess

from .attacks import get_least_valuable_attacker
from .exchange import get_exchange_evaluation
from .values import get_square_value


def is_hanging(board: chess.Board, square: chess.Square) -> bool:
    """Return True if a piece at *square* is hanging."""
    if board.piece_type_at(square) is None:
        return False

    return get_exchange_evaluation(board, not board.color_at(square), square) > 0


def get_hanging_pieces(board: chess.Board, color: chess.Color) -> chess.SquareSet:
    """Return a SquareSet of hanging pieces of a certain color."""
    pieces = chess.SquareSet(board.occupied_co[color])
    king = board.king(color)
    if king is not None:
        pieces.remove(king)
    hanging = chess.SquareSet()
    for piece in pieces:
        if is_hanging(board, piece):
            hanging.add(piece)
    return hanging


def get_hanging_after_move(
    board: chess.Board, move: chess.Move, color=None
) -> chess.SquareSet:
    """
    Return a SquareSet of pieces of a certain color which are hanging
    after a *move*.
    By default, the color of the moved piece is used.
    """
    if color is None:
        color = board.color_at(move.from_square)
    board_copy = board.copy()
    board_copy.push(move)
    return get_hanging_pieces(board_copy, color)


def can_be_captured(board: chess.Board, square: chess.Square) -> bool:
    """Return True if a piece at *square* can be captured. This includes
    cases where
    * the piece is hanging,
    * the piece is not hanging, but can be traded off on equal terms.
    """
    if is_hanging(board, square):
        return True

    opponent_color = not board.color_at(square)
    attacker = get_least_valuable_attacker(board, opponent_color, square)
    if attacker is not None:
        attacker_value = get_square_value(board, attacker)
        piece_value = get_square_value(board, square)
        # We already know the piece is not hanging. So, to trade it off, the
        # attacker value should be equal to the piece value (<= is just in case).
        if attacker_value <= piece_value:
            return True

    return False


def is_fork(board: chess.Board, square: chess.Square) -> bool:
    """Return True if a piece at *square* is forking."""
    # the piece shouldn't be hanging, and it shouldn't be possible to
    # trade it off
    if can_be_captured(board, square):
        return False

    # 2+ pieces attacked by this piece should be hanging
    forked = _get_attacked_hanging(board, square)
    return len(forked) > 1


def is_forking_move(board: chess.Board, move: chess.Move) -> bool:
    """Return True if a move is a fork."""
    board_after = board.copy()
    board_after.push(move)

    # the moved piece shouldn't be hanging, and it shouldn't be possible to
    # trade it off
    if can_be_captured(board_after, move.to_square):
        return False

    # there should be at least 2 more hanging pieces after the move,
    # attacked by the moved piece
    hanging_after = _get_attacked_hanging(board_after, move.to_square)

    hanging_before = chess.SquareSet()
    for piece in hanging_after:
        if is_hanging(board, piece):
            hanging_before.add(piece)

    forked = hanging_after - hanging_before
    return len(forked) > 1


def _get_attacked_hanging(board: chess.Board, square: chess.Square) -> chess.SquareSet:
    color = not board.color_at(square)
    attacked = chess.SquareSet(board.attacks_mask(square) & board.occupied_co[color])
    return chess.SquareSet([s for s in attacked if is_hanging(board, s)])
