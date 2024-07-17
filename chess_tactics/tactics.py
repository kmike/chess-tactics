import chess

from .exchange import push_exchange


def is_hanging(board: chess.Board, sqaure: chess.Square) -> bool:
    """Return True if a piece at *square* is hanging."""
    if board.piece_type_at(sqaure) is None:
        return False

    board_copy = board.copy()
    push_exchange(board_copy, not board_copy.color_at(sqaure), sqaure)
    return len(board_copy.move_stack) > len(board.move_stack)


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
