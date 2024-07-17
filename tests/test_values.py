import chess

from chess_tactics.values import get_piece_value, get_square_value


def test_get_square_value():
    board = chess.Board()
    assert get_square_value(board, chess.A1) == 5
    assert get_square_value(board, chess.B7) == 1


def test_get_piece_value():
    board = chess.Board()
    rook = board.piece_at(chess.A1)
    assert get_piece_value(rook) == 5

    pawn = board.piece_at(chess.B7)
    assert get_piece_value(pawn) == 1
