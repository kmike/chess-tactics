import chess

PIECE_VALUES = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 1000,
    None: 0,
}


def get_square_value(board: chess.Board, square: chess.Square) -> int:
    return PIECE_VALUES[board.piece_type_at(square)]
