import chess
import pytest

from chess_tactics.mistakes import (
    hanging_piece_not_captured,
    hung_moved_piece,
    hung_other_piece,
    missed_fork,
    started_bad_trade,
)

from .fens import EXAMPLE_01


@pytest.mark.parametrize(
    ["fen", "move_san", "best_moves_san", "expected"],
    [
        # basic cases
        ("1k6/8/8/4p3/8/2B5/8/1K6 w - - 0 1", "Bb2", ["Bxe5"], True),
        ("1k6/8/8/4p3/8/2B5/8/1K6 w - - 0 1", "Bxe5", ["Bxe5"], False),
        # piece is captured, but a different one, with the same value
        ("1k6/8/8/p3p3/8/2B5/8/1K6 w - - 0 1", "Bxa5", ["Bxe5"], False),
        # a piece with a lower value is captured: what to do here?
        pytest.param(
            "1k6/8/8/p3n3/8/2B5/8/1K6 w - - 0 1",
            "Bxa5",
            ["Bxe5"],
            False,
            marks=pytest.mark.skip(),
        ),
        # a piece is protected insufficiently
        ("1k6/5n2/8/4p3/8/2B5/8/QK6 w - - 0 1", "Bb2", ["Bxe5"], True),
        # a piece is not protected (and is not captured), but the best move
        # is not a capture
        ("1k6/8/8/4p3/8/2B5/8/1K6 w - - 0 1", "Bb2", ["Bb4"], False),
        # Assorted example 1
        (
            "2r3k1/pp6/3bpr1p/3p1ppq/3P1P2/2P2NQ1/PP4PP/R4RK1 b - - 1 21",
            "Kg7",
            ["Bxf4"],
            True,
        ),
        # Assorted example 2
        (
            "r2qB1k1/2p2p2/1p2p1p1/p3P2p/3P4/b1P2Q2/P4PPP/R3R1K1 w - - 0 18",
            "Bc6",
            ["Qxf7"],
            True,
        ),
        # Assorted example 3
        (
            "r2qkbnr/p3pppp/2p5/np1PN2b/P1p1P3/8/1PQ2PPP/RNB1KB1R b KQkq - 0 9",
            "Qd6",
            ["cxd5"],
            True,
        ),
        # Blunder, but a different one. Hanging piece was captured,
        # but it loses a qqueen.
        (
            "r2qkbnr/p3pppp/2p5/np1PN2b/P1p1P3/8/1PQ2PPP/RNB1KB1R b KQkq - 0 9",
            "Qxd5",
            ["cxd5"],
            False,
        ),
        # Assorted example 4, with a pinned defender
        (
            "r1bqkb1r/pp3pp1/2n4p/4p3/Q3P3/2P2N2/P4PPP/R1B1KB1R w KQkq - 0 12",
            "Bb5",
            ["Nxe5"],
            True,
        ),
        # Assorted example 5
        (
            "r1b1k2r/pp3ppp/2n1p3/8/1bBP4/q3PN2/P2N2PP/R2Q1RK1 b kq - 5 13",
            "O-O",
            ["Qxe3"],
            True,
        ),
        # Assorted example 6
        (
            "r1b1kb1r/ppq2ppp/2n1p3/3pPn2/N2P4/5N2/PP1BBPPP/R2Q1RK1 b kq - 7 11",
            "a6",
            ["Nfxd4"],
            True,
        ),
        # Assorted example 7: pawn is hanging tactically, not directly,
        # so it's not considered hanging (it'd be a missed sacrifice)
        (
            "2kr3r/pp2pp2/2q2bp1/8/2PPR3/1P3NPp/P3QP1P/R5K1 b - - 0 19",
            "g5",
            ["Bxd4"],
            False,
        ),
        # Assorted example 8
        (
            "1k1r3r/pb2n1qp/1p6/4bQ2/2P2p2/P2B4/1P3PPP/1RB1R1K1 w - - 10 26",
            "Qh3",
            ["Qxe5"],
            True,
        ),
    ],
)
def test_hanging_piece_not_captured(fen, move_san, best_moves_san, expected):
    board, move, best_moves = _board_move_best_moves(fen, move_san, best_moves_san)
    assert hanging_piece_not_captured(board, move, best_moves) is expected


@pytest.mark.parametrize(
    ["fen", "move_san", "best_opponent_moves_san", "expected"],
    [
        # basic cases
        (EXAMPLE_01, "Bd4", [], True),
        (EXAMPLE_01, "Bb2", [], False),
        # bad trade is a sepatate mistake
        (EXAMPLE_01, "Bxe5", [], False),
        # If, for some reason, capturing is not the best move for the opponent,
        # a move is no longer considered as a mistake of this type
        (EXAMPLE_01, "Bd4", ["e4"], False),
        # Assorted example 1
        (
            "r3k2r/1p3pb1/p1n1p1pp/3q4/3PnB2/N2Q1N1P/PP3PP1/2R1R1K1 b kq - 1 17",
            "Nc5",
            [],
            True,
        ),
        # Assorted example 2: a pawn is lost in the exchange
        (
            "r4rk1/p1p2p1p/2p1p1p1/3nP3/3PN2q/P4P2/1P1Q1P1P/R3K2R w KQ - 0 16",
            "Nf6",
            [],
            True,
        ),
        # Assorted example 3: attacker forgot that a piece is no longer pinned.
        # it's not "hung_moved_piece", it's a bad trade, because there was
        # a capture.
        (
            "r2qkb1r/pp1b1pp1/2n4p/1B2p3/Q3P3/2P2N2/P4PPP/R1B1K2R w KQkq - 2 13",
            "Nxe5",
            [],
            False,
        ),
        # Assorted example 4: there is a pin, but 1) it doesn't work tactically,
        # and 2) relative pins are not handled by this heuristic
        (
            "r4b1r/2k3p1/pp1p1pbp/Q1pP4/5q2/2N2N1P/PP3PP1/2R1R1K1 w - - 0 20",
            "Nb5",
            [],
            True,
        ),
        # Assorted example 5: piece was hanging before the move, and it's
        # hanging after the move.
        (
            "r4b1r/1k4p1/pp1p1pbp/QNpP4/5q2/5N1P/PP3PP1/2R1R1K1 w - - 2 21",
            "Qa4",
            [],
            True,
        ),
        # Assorted example 6
        (
            "8/1kr2pp1/p1pr3p/P2pNn1P/1P3P2/1R2P3/2P1KP2/3R4 w - - 3 38",
            "b5",
            [],
            True,
        ),
        # Assorted example 7
        (
            "r3r1k1/p4p1p/3p2p1/2pPnbq1/2P5/P1Q5/4BPPP/R3R1K1 w - - 0 19",
            "Rab1",
            [],
            True,
        ),
        # Assorted example 8
        (
            "r1b2r2/5k2/p3qp2/2p1p2R/P3P2B/2P2QK1/8/R7 w - - 2 34",
            "Qg4",
            [],
            True,
        ),
    ],
)
def test_hung_moved_piece(fen, move_san, best_opponent_moves_san, expected):
    board, move, best_opponent_moves = _board_move_best_moves(fen, move_san, [])
    best_opponent_moves = _best_opponent_moves(board, move, best_opponent_moves_san)
    assert hung_moved_piece(board, move, best_opponent_moves) is expected


@pytest.mark.parametrize(
    ["fen", "move_san", "best_opponent_moves_san", "expected"],
    [
        # basic cases
        (EXAMPLE_01, "Bxe5", [], True),
        (EXAMPLE_01, "Bb2", [], False),
        # hanging a piece without a capture is considered a separate mistake
        (EXAMPLE_01, "Bd4", [], False),
        # If, for some reason, recapturing is not the best move for the opponent,
        # a move is no longer considered as a mistake of this type
        (EXAMPLE_01, "Bxe5", ["Kb7"], False),
        # Assorted example 1: attacker forgot that a piece is no longer pinned,
        # and captured a pawn
        (
            "r2qkb1r/pp1b1pp1/2n4p/1B2p3/Q3P3/2P2N2/P4PPP/R1B1K2R w KQkq - 2 13",
            "Nxe5",
            [],
            True,
        ),
        # Assorted example 2: someone thought it's a pin
        (
            "r3k2r/pp3pp1/1qnbpnp1/3p2B1/3P2P1/1QP4P/PP1N1PB1/R3K2R b KQkq - 7 15",
            "Nxg4",
            [],
            True,
        ),
        # The same, but there is really a pin this time. It's still
        # considered as a bad trade, as this heuristic doesn't handle
        # relative pins.
        (
            "r3k2r/pp3pp1/1qnbpnp1/3p2B1/3P2P1/1QP4P/PP1N1P2/R3K2R b KQkq - 7 15",
            "Nxg4",
            [],
            True,
        ),
        # Assorted example 3
        (
            "8/2r2pp1/k2r3p/Pppp1n1P/5P2/1R1NP3/2P1KP2/R7 w - - 0 41",
            "Nxc5",
            [],
            True,
        ),
        # Assorted example 4: counting error
        (
            "6r1/pp5k/4p1q1/3pPp2/6rp/2P1Q3/PP2RRPP/6K1 b - - 3 30",
            "Rxg2",
            [],
            True,
        ),
        # This would have been a good trade
        (
            "6r1/pp5k/4p1q1/3pPp2/6rp/2P1Q3/PP3RPP/6K1 b - - 3 30",
            "Rxg2",
            [],
            False,
        ),
        # Assorted example 5
        (
            "r3k2r/pbpp1qpp/1pnbp3/3N4/2PP1p2/P2B1N2/1P2QPPP/R1B1K2R w KQkq - 4 14",
            "Nxc7",
            [],
            True,
        ),
    ],
)
def test_started_bad_trade(fen, move_san, best_opponent_moves_san, expected):
    board, move, best_opponent_moves = _board_move_best_moves(fen, move_san, [])
    best_opponent_moves = _best_opponent_moves(board, move, best_opponent_moves_san)
    assert started_bad_trade(board, move, best_opponent_moves) is expected


@pytest.mark.parametrize(
    ["fen", "move_san", "best_moves_san", "expected"],
    [
        # Dropped defence
        (
            "3qr1k1/4bpp1/5n1p/r1p5/2Q5/4BN2/P4PPP/R3R1K1 b - - 1 22",
            "Kh8",
            ["Bf8"],
            True,
        ),
        # Dropped defence, but the best move also drops the defence for some reason
        (
            "3qr1k1/4bpp1/5n1p/r1p5/2Q5/4BN2/P4PPP/R3R1K1 b - - 1 22",
            "Kh8",
            ["Kh7"],
            False,
        ),
        # Dropped defence with a capture
        (
            "r2qk1nr/ppp1ppbp/2np2p1/8/2PPP3/2N1Bb2/PP3PPP/R2QKB1R w KQkq - 0 7",
            "Qxf3",
            ["gxf3"],
            True,
        ),
        # Defence is not dropped
        (
            "r2qk1nr/ppp1ppbp/2np2p1/8/2PPP3/2N1Bb2/PPN2PPP/R2QKB1R w KQkq - 0 7",
            "Qxf3",
            ["gxf3"],
            False,
        ),
        # Defence is dropped because of a pin
        (
            "2r2rk1/p2n1pp1/b3pn1p/q7/P1PP4/3Q1PB1/4B1PP/2R1K2R w K - 1 21",
            "Rc3",
            ["Qd2"],
            True,
        ),
        # Defence is dropped (c4), but the best move also drops the defence (a3)
        (
            "2r2rk1/p2n1pp1/b3pn1p/q7/2PP4/P2Q1PB1/4B1PP/2R1K2R w K - 1 21",
            "Rc3",
            ["Qd2"],
            False,
        ),
        # Block is removed
        (
            "rnbqk1nr/ppppppbp/6p1/8/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 0 1",
            "b3",
            ["d4"],
            True,
        ),
        # Pin on the attacker is removed
        (
            "r1bqkbnr/pp3ppp/2n1p3/1BppP3/3P4/2P2Q2/PP3PPP/RNB1K1NR w KQkq - 0 1",
            "Bd3",
            ["Ne2"],
            True,
        ),
        # Best move hangs less value than the move which is made (pawn vs bishop)
        (
            "r4b1r/pp1k1pp1/3p2bp/2pP4/1q2NB2/5N1P/PP2QPP1/R4RK1 w - - 3 15",
            "Nc3",
            ["Nfd2"],
            True,
        ),
        # Assorted examples
        (
            "3r2k1/2r2pp1/1p3p1p/p1b5/P1RPP1B1/6P1/5P1P/3R2K1 b - - 0 27",
            "Bb4",
            ["Bd6"],
            True,
        ),
        (
            "8/p7/4pkp1/5p1p/r4P2/P1R2PK1/7P/8 w - - 1 32",
            "Kf2",
            ["h4"],
            True,
        ),
    ],
)
def test_hung_other_piece(fen, move_san, best_moves_san, expected):
    board, move, best_moves = _board_move_best_moves(fen, move_san, best_moves_san)
    assert hung_other_piece(board, move, best_moves) is expected


@pytest.mark.parametrize(
    ["fen", "move_san", "best_moves_san", "fork_missing"],
    [
        ("k7/8/1q3r2/8/8/4N3/2K5/8 w - - 0 1", "Nc4", ["Nd5"], True),
        ("k7/8/1q3r2/8/8/4N3/2K5/8 w - - 0 1", "Nd5", ["Nd5"], False),
        # best move is not a fork
        ("k7/8/1q3r2/8/8/4N3/2K5/8 w - - 0 1", "Nc4", ["Kd2"], False),
        # fork is found, but not the best one
        ("k7/8/1q3r2/8/8/r3N3/2K5/8 w - - 0 1", "Nc4", ["Nd5"], False),
        # multiple best moves
        ("k7/8/1q3r2/8/8/r3N3/2K5/8 w - - 0 1", "Ng2", ["Kd2", "Nd5"], True),
        # Assorted example 1
        (
            "2k4r/pp1rpQ1p/2pp2pn/4P3/1RP5/2PB4/q4PPP/1R4K1 w - - 1 17",
            "Qe6",
            ["Qg7"],
            True,
        ),
        # Assorted example 2: crazy Rxe5 fork - both pawns are hanging because
        # of the discovered attack. Should we consider such cases forks?
        (
            "r4rk1/pp1nq1pp/3p4/2pn4/2Q5/5P2/PPP2PPP/2KR1B1R w - - 0 13",
            "Rxd5",
            ["Qxd5"],
            False,
        ),
        # Assorted example 3
        (
            "5rk1/pRQ3pp/6r1/8/3nN3/P4PP1/q3PK1P/4R3 b - - 4 28",
            "Qe6",
            ["Nxf3"],
            True,
        ),
        # Assorted example 4
        (
            "r7/P1r2ppp/3kp1b1/8/8/2N5/1P2BPPP/R4RK1 w - - 2 27",
            "Rfd1",
            ["Nb5"],
            True,
        ),
        # Assorted example 5
        (
            "r4rk1/q5pp/pb2p3/1p1pP1N1/1P1Pb3/P1R1Q3/4BPPP/2R3K1 b - - 2 25",
            "Bf5",
            ["Bxd4"],
            True,
        ),
        # Assorted example 6
        (
            "1k1r3r/5pp1/p1pp3p/P2N1q2/4n1b1/4PN2/1PP2PPP/R2Q1RK1 w - - 0 17",
            "Nb6",
            ["Nb4"],
            True,
        ),
        # Assorted example 7
        (
            "2rq1rk1/4b1pp/p3p3/1p1bPp2/3P1P2/P3BB1P/6P1/R2Q1RK1 b - - 1 22",
            "Bc4",
            ["Rc3"],
            True,
        ),
    ],
)
def test_missed_fork(fen, move_san, best_moves_san, fork_missing):
    board, move, best_moves = _board_move_best_moves(fen, move_san, best_moves_san)
    assert missed_fork(board, move, best_moves) is fork_missing


def _board_move_best_moves(
    fen: str, move_san: str, best_moves_san: list[str]
) -> tuple[chess.Board, chess.Move, list[chess.Move]]:
    board = chess.Board(fen)
    move = board.parse_san(move_san)
    best_moves = [board.parse_san(m) for m in best_moves_san]
    return board, move, best_moves


def _best_opponent_moves(
    board: chess.Board, move: chess.Move, best_opponent_moves_san: list[str]
) -> list[chess.Move]:
    board_after_move = board.copy()
    board_after_move.push(move)
    return [board_after_move.parse_san(m) for m in best_opponent_moves_san]
