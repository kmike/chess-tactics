import chess

from .exchange import get_exchange_evaluation


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
