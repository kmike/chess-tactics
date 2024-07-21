"""
Some utilities for lichess JSON games.
"""

from typing import Optional

import chess
import chess.engine

# Engine limits which Lichess uses for the manually requested computer
# analysis. See
# https://github.com/lichess-org/lila/blob/5ed87699dad51ccf06e103f712fc304c009fed51/modules/fishnet/src/main/Work.scala#L72
EVAL_LIMIT = chess.engine.Limit(nodes=1_000_000)


def game_to_board(game) -> chess.Board:
    board = chess.Board()
    for move in game["moves"].split():
        board.push_san(move)
    return board


def eval_to_score(lichess_eval) -> chess.engine.Score:
    """Convert "eval" from Lichess JSON API game analysis entry"""
    if "eval" in lichess_eval:
        return chess.engine.Cp(lichess_eval["eval"])
    elif "mate" in lichess_eval:
        return chess.engine.Mate(lichess_eval["mate"])
    else:
        raise ValueError("No evaluation available")


def eval_to_best_move(lichess_eval) -> Optional[chess.Move]:
    """Extract best move from Lichess JSON API game analysis entry"""
    if "best" in lichess_eval:
        return chess.Move.from_uci(lichess_eval["best"])
    return None


def get_user_colors(game) -> dict[Optional[str], chess.Color]:
    """Return ``{"user1": chess.WHITE, "user2": chess.BLACK}`` dictionary."""
    players = game["players"]

    def _get_id(color):
        if "user" in players[color]:
            return players[color]["user"]["id"]
        else:
            return None

    return {
        _get_id("white"): chess.WHITE,
        _get_id("black"): chess.BLACK,
    }


# def get_winner(game):
#     if game["status"] in {"draw", "stalemate"}:
#         return None
#     if "winner" not in game:
#         print(game)
#     return game["players"][game["winner"]]["user"]["id"]
