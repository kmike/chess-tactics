import chess
import pytest
from chess.engine import Cp, Mate

from chess_tactics.lichess_game import (
    eval_to_best_move,
    eval_to_score,
    game_to_board,
    get_user_colors,
)

from ._lichess_games import GAME_1


def test_game_to_board():
    board = game_to_board(GAME_1)
    assert len(board.move_stack) == 52
    assert board.fen() == "r5k1/pp4q1/8/7p/3NpB2/2QnP2b/PP6/3R2K1 w - - 2 27"


@pytest.mark.parametrize(
    ["lichess_eval", "expected_score"],
    [
        ({"eval": 119}, Cp(119)),
        (
            {
                "eval": -62,
                "best": "a1c1",
                "variation": "Rc1 Ne5 Nb5 h6 Bh4 Bd7 Nc7 d4 Qxd4 Nc6 Bxf6 gxf6",
                "judgment": {
                    "name": "Inaccuracy",
                    "comment": "Inaccuracy. Rc1 was best.",
                },
            },
            Cp(-62),
        ),
        ({"mate": -2}, Mate(-2)),
        ({"mate": 1}, Mate(1)),
    ],
)
def test_eval_to_score(lichess_eval, expected_score):
    assert eval_to_score(lichess_eval) == expected_score


def test_eval_to_best_move():
    assert eval_to_best_move({"eval": 119}) is None
    assert eval_to_best_move(
        {
            "eval": 62,
            "best": "a1c1",
            "variation": "Rc1 Ne5 Nb5 h6 Bh4 Bd7 Nc7 d4 Qxd4 Nc6 Bxf6 gxf6",
            "judgment": {"name": "Inaccuracy", "comment": "Inaccuracy. Rc1 was best."},
        }
    ) == chess.Move(from_square=chess.A1, to_square=chess.C1)


def test_get_user_colors():
    assert get_user_colors(GAME_1) == {"kmike84": chess.WHITE, "opponent": chess.BLACK}
