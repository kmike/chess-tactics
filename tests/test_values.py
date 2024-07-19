import chess

from chess_tactics.values import get_square_value


def test_get_square_value():
    board = chess.Board()
    assert get_square_value(board, chess.A1) == 5
    assert get_square_value(board, chess.B7) == 1
