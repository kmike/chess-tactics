import chess


def pytest_assertrepr_compare(op, left, right):
    """Nice display for SquareSet asserts"""
    if (
        isinstance(left, chess.SquareSet)
        and isinstance(right, chess.SquareSet)
        and op == "=="
    ):
        lines = ["Comparing chess.SquareSet instances:"]
        left_rows, right_rows = str(left).splitlines(), str(right).splitlines()
        for idx, (left_row, right_row) in enumerate(zip(left_rows, right_rows)):
            if idx == 4:
                lines.append(f"{left_row}    !=    {right_row}")
            else:
                lines.append(f"{left_row}          {right_row}")
        return lines
