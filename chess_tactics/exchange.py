import chess

from .attacks import get_least_valuable_attacker
from .utils import running_total
from .values import get_square_value


def push_exchange(
    board: chess.Board, color: chess.Color, square: chess.Square
) -> float:
    """
    Simulate an exchange at ``square``, started by ``color``, and push the
    moves to the board.

    Both players try to be reasonable and avoid material loss, i.e.
    unfavorable captures shouldn't happen (including the first move).
    Equal trades are also avoided.

    This is based on pure piece values, not on the engine eval.

    Returns the value of the exchange which happened.
    """
    moves, captured_piece_values = _greedy_exchange(board, color, square)
    n_moves_greedy = len(moves)
    n_moves_proper = _times_to_capture(captured_piece_values)

    for _ in range(n_moves_greedy - n_moves_proper):
        board.pop()

    return sum(captured_piece_values[:n_moves_proper])


def get_exchange_value(board: chess.Board, move: chess.Move) -> float:
    """Return the value of a potential exchange started by *move*.

    Only captures at the target square are considered.
    The move is not checked for legality.
    """
    board = board.copy()
    captured_value = get_square_value(board, move.to_square)
    board.push(move)
    opponent_color = not board.color_at(move.to_square)
    recaptured_value = push_exchange(board, opponent_color, move.to_square)
    return captured_value - recaptured_value


def _greedy_exchange(
    board: chess.Board, color: chess.Color, square: chess.Square
) -> tuple[list[chess.Move], list[float]]:
    """
    Simulate the exchange at square, started by color.

    Each player keeps capturing until there are no pieces which can capture.
    Each time the least valuable attacker is used to capture.
    """
    attacker_color = color
    captured_piece_values = []
    moves = []
    while True:
        attacker = get_least_valuable_attacker(board, color, square)
        if attacker is None:
            break

        captured_piece_value = get_square_value(board, square)
        if color != attacker_color:
            captured_piece_value = -captured_piece_value
        captured_piece_values.append(captured_piece_value)

        move = chess.Move(from_square=attacker, to_square=square)
        board.push(move)
        moves.append(move)
        color = not color

    return moves, captured_piece_values


def _times_to_capture(captured_values) -> int:
    """
    Return the number of times capture should happen during the exchange,
    assuming the players are reasonable: unfavorable captures shouldn't happen,
    from both sides (including the first capture).

    Equal trades are also avoided.
    """
    # The code is quite tricky; can it be written in a simpler way?

    def attacker_times_to_capture(values_total):
        if not values_total:
            return 0

        values_total_padded = values_total[:]
        if len(values_total) % 2:
            values_total_padded.append(values_total[-1])

        value_diff_after_opponent_move = values_total_padded[1::2]

        best_idx = max(
            range(0, len(value_diff_after_opponent_move)),
            key=lambda idx: value_diff_after_opponent_move[idx],
        )
        best_value_diff = value_diff_after_opponent_move[best_idx]

        if best_value_diff > 0:
            return best_idx + 1
        else:
            return 0

    # only consider captures defender is willing to perform
    defending_pov_values = [-v for v in captured_values[1:]]
    defending_pov_totals = running_total(defending_pov_values)
    def_times = attacker_times_to_capture(defending_pov_totals)
    max_length = 1 + def_times * 2
    captured_values = captured_values[:max_length]

    # how many times attacker should capture?
    values_total = running_total(captured_values)
    att_times = attacker_times_to_capture(values_total)

    if att_times == 0:
        return 0
    return att_times * 2 - len(captured_values) % 2
