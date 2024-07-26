import chess


def san_list_to_moves(board: chess.Board, san_list: list[str]) -> list[chess.Move]:
    """Convert a list of strings with SANs to a list of chess.Move instances"""
    board = board.copy()
    moves = []
    for san in san_list:
        move = board.parse_san(san)
        board.push(move)
        moves.append(move)
    return moves


def moves_to_san_list(board: chess.Board, moves: list[chess.Move]) -> list[str]:
    """Convert a list of chess.Move instances to a list of strings with SANs"""
    board = board.copy()
    san_list = []
    for move in moves:
        san = board.san(move)
        board.push(move)
        san_list.append(san)
    return san_list
