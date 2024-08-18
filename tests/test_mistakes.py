from typing import Optional

import chess
import pytest
from chess.engine import Cp, Mate

from chess_tactics.lichess_game import get_lichess_analyze_link
from chess_tactics.mistakes import (
    hanging_piece_not_captured,
    hung_fork,
    hung_mate_n,
    hung_mate_n_plus,
    hung_moved_piece,
    hung_other_piece,
    left_piece_hanging,
    missed_fork,
    missed_mate_n,
    missed_mate_n_plus,
    missed_sacrifice,
    started_bad_trade,
)
from chess_tactics.move_utils import moves_to_san_list, san_list_to_moves

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
        # Example from left_piece_hanging tests
        (
            "r3k2r/1p3pb1/p1n1p1pp/3q4/3PnB2/N2Q1N1P/PP3PP1/2R1R1K1 b kq - 1 17",
            "Nc5",
            ["Rxc5"],
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
        # Assorted example 8: looks almost like a fork, but not really
        (
            "r2q1rk1/1p1bbppp/p1n1p3/4P3/3P4/3B1N2/P1Q2PPP/R1B2RK1 b - - 2 13",
            "f6",
            ["Nb4"],
            False,
        ),
    ],
)
def test_missed_fork(fen, move_san, best_moves_san, fork_missing):
    board, move, best_moves = _board_move_best_moves(fen, move_san, best_moves_san)
    assert missed_fork(board, move, best_moves) is fork_missing


@pytest.mark.parametrize(
    ["fen", "move_san", "best_opponent_moves_san", "pv_san_list", "expected"],
    [
        # Example 1
        (
            "r3k2r/ppp2pp1/2n1q2p/3N3P/4n3/1P3N2/PKP1QPP1/3R3R b kq - 0 15",
            "Nd6",
            ["Nxc7"],
            ["O-O-O", "Nc3", "f5", "Nxe4", "fxe4", "Nd2"],
            True,
        ),
        # Example 1, modified (best move for the opponent is not a fork)
        (
            "r3k2r/ppp2pp1/2n1q2p/3N3P/4n3/1P3N2/PKP1QPP1/3R3R b kq - 0 15",
            "Nd6",
            ["Qb5"],
            ["O-O-O", "Nc3", "f5", "Nxe4", "fxe4", "Nd2"],
            False,
        ),
        # Example 1, modified (opponent forks even after the best response)
        (
            "r3k2r/ppp2pp1/2n1q2p/3N3P/4n3/1P3N2/PKP1QPP1/3R3R b kq - 0 15",
            "Nd6",
            ["Nxc7"],
            ["Qf5", "Nxc7"],
            False,
        ),
        # Example 1, modified (principal variation is not available)
        (
            "r3k2r/ppp2pp1/2n1q2p/3N3P/4n3/1P3N2/PKP1QPP1/3R3R b kq - 0 15",
            "Nd6",
            ["Nxc7"],
            None,
            True,
        ),
        # Example 1, modified (principal variation is not fully available)
        (
            "r3k2r/ppp2pp1/2n1q2p/3N3P/4n3/1P3N2/PKP1QPP1/3R3R b kq - 0 15",
            "Nd6",
            ["Nxc7"],
            ["O-O-O"],
            True,
        ),
        # Example 2, simple
        (
            "r1b2rk1/pp3p1p/4p1p1/4N1Qn/3q4/3B4/PP3PPP/R4RK1 w - - 0 19",
            "Rad1",
            ["fxf6"],
            ["Qe3", "Qxb2", "Rfe1"],
            True,
        ),
        # Example 3
        (
            "r4r1k/pp1nq1pp/3p4/2pR4/2Q5/5P2/PPP2PPP/2K2B1R w - - 1 14",
            "Bd3",
            ["Nxb6"],
            ["Qe4", "Qf6", "Rd1", "Rad8", "Bd3"],
            True,
        ),
        # Example 4
        (
            "8/prp1R3/8/3kp1r1/5p2/5K2/P4P2/8 w - - 0 34",
            "a3",
            ["Rxb3"],
            ["Rd7+", "Ke6", "Rh7", "Rg1"],
            True,
        ),
        # Example 5 (queen fork)
        (
            "6r1/4k2p/p1q1pn1Q/1p6/8/PP3P2/7P/5R1K b - - 0 30",
            "Ng4",
            ["Qxh7"],
            ["Qc2", "Rg1", "Rxg1+", "Kxg1"],
            True,
        ),
        # Example 6 (this also hangs a piece and hangs a mate)
        (
            "r1b2r2/5k2/p3qp2/2p1p2R/P3P2B/2P2QK1/8/R7 w - - 2 34",
            "Qg4",
            ["Qexg4"],
            ["Rh7+", "Kg8"],
            True,
        ),
    ],
)
def test_hung_fork(fen, move_san, best_opponent_moves_san, pv_san_list, expected):
    board, move, _ = _board_move_best_moves(fen, move_san)
    best_opponent_moves = _best_opponent_moves(board, move, best_opponent_moves_san)
    pv = san_list_to_moves(board, pv_san_list) if pv_san_list else None
    assert hung_fork(board, move, best_opponent_moves, pv) is expected


@pytest.mark.parametrize(
    ["fen", "move_san", "best_moves_san", "expected"],
    [
        # Basic cases
        ("k7/6b1/8/4B3/8/8/8/1K6 w - - 0 1", "Kc1", ["Bxg7"], True),
        ("k7/6b1/8/4B3/8/8/8/1K6 w - - 0 1", "Bxg7", ["Bxg7"], False),
        ("k7/6b1/8/4B3/8/8/8/1K6 w - - 0 1", "Bxf4", ["Bxf4"], False),
        # two pieces hanging, more valuable should be protected / moved
        ("7k/8/5b2/8/7P/8/1N6/3K4 w - - 0 1", "Nc4", ["Nd3"], False),
        ("7k/8/5b2/8/7P/8/1N6/3K4 w - - 0 1", "h5", ["Nd3"], True),
        # if possible, both should be protected - saving one is not enough
        ("7k/8/5b2/8/3N3P/8/8/3K4 w - - 0 1", "Nf3", ["Nf3"], False),
        ("7k/8/5b2/8/3N3P/8/8/3K4 w - - 0 1", "Nc6", ["Nf3"], True),
        # Basic cases should work if best_moves are not available
        ("k7/6b1/8/4B3/8/8/8/1K6 w - - 0 1", "Kc1", None, True),
        ("k7/6b1/8/4B3/8/8/8/1K6 w - - 0 1", "Bxg7", None, False),
        ("k7/6b1/8/4B3/8/8/8/1K6 w - - 0 1", "Bxf4", None, False),
        # Trading off the hanging piece is a way to save it
        ("k6p/n5b1/8/8/3B2n1/8/5p2/1K6 w - - 0 1", "Bxg7", ["Bxa7"], False),
        ("k6p/n5b1/8/8/3B2n1/8/5p2/1K6 w - - 0 1", "Bxg7", None, False),
        # it matters what to trade for, but if the hanging piece is moved,
        # it's not "left hanging"
        ("k6p/n5b1/8/8/3B2n1/8/5p2/1K6 w - - 0 1", "Bxf2", ["Bxa7"], False),
        # If there are multiple pieces hanging, saving one of them
        # is better than saving nothing.
        pytest.param(
            "kr6/pn5p/1p4N1/2p5/3N4/8/8/1K6 w - - 0 1",
            "Kc2",
            ["Nb5"],
            True,
            marks=pytest.mark.xfail(reason="Not implemented"),
        ),
        pytest.param("kr6/pn5p/1p4N1/2p5/3N4/8/8/1K6 w - - 0 1", "Ne6", ["Nb5"], False),
        # Similar examples with multiple pieces, but different outcome,
        # because by setting up re-capture we're getting a pawn.
        ("kr6/pn5p/1p4p1/2p2R2/3R4/8/8/1K6 w - - 0 1", "Kc2", ["Rdd5"], True),
        ("kr6/pn5p/1p4p1/2p2R2/3R4/8/8/1K6 w - - 0 1", "Rdf4", ["Rdd5"], False),
        pytest.param(
            "kr6/pn5p/1p4p1/2p2R2/3R4/8/8/1K6 w - - 0 1",
            "Rd7",
            ["Rdd5"],
            False,
            marks=pytest.mark.xfail(
                reason="Rd7 counter-attacks h7, but it doesn't count (as it's not "
                "implemented), while Rdd5 changes the exchange value at f5, "
                "which counts. So, the heuristic wrongly thinks we haven't "
                "saved enough material."
            ),
        ),
        # If pieces of different value are hanging, the most valuable should be
        # saved first
        ("kr6/pn5p/1p4p1/2p2B2/3R4/8/8/1K6 w - - 0 1", "Rf4", ["Rd5"], False),
        ("kr6/pn5p/1p4p1/2p2B2/3R4/8/8/1K6 w - - 0 1", "Bg4", ["Rd5"], True),
        # Best move is not to save a piece
        ("8/3Q2b1/1K6/4B3/r7/8/8/3B1k2 w - - 0 1", "Qxa4", ["Qxa4"], False),
        ("8/3Q2b1/1K6/4B3/r7/8/8/3B1k2 w - - 0 1", "Bd6", ["Qxa4"], False),
        ("8/3Q2b1/1K6/4B3/r7/8/8/3B1k2 w - - 0 1", "Qc6", ["Qxa4"], True),
        ("8/3Q2b1/1K6/4B3/r7/8/8/3B1k2 w - - 0 1", "Bxa4", ["Qxa4"], False),
        ("8/3Q2b1/1K6/4B3/r7/8/8/3B1k2 w - - 0 1", "Qd4", ["Qxa4"], True),
        # If the moved piece was hanging before the move, and hangs after,
        # it's considered "hang_moved_piece", not "left_piece_hanging"
        ("1k6/5p2/1p6/2N5/8/8/5K2/8 w - - 0 1", "Ne6", ["Nd7"], False),
        ("1k6/5p2/1p2p3/2N5/8/8/5K2/8 w - - 0 1", "Ne6", ["Nd7"], False),
        # Assorted example 1
        (
            "rn1qkb1r/pp2ppp1/2p2np1/8/2pP4/2N5/PPQ1PPPP/R1B1KB1R w KQkq - 0 8",
            "a4",
            ["e3"],
            True,
        ),
        # Assorted example 2
        (
            "r1b2rk1/pp2n1pp/1qnp4/5p2/8/2N2NP1/PPP1PPBP/R2QK2R w KQ - 4 10",
            "a3",
            ["b3"],
            True,
        ),
        # Assorted example 3, pins everywhere
        (
            "5rk1/pRQ3pp/6r1/8/3nN3/P4PP1/q3P1KP/4R3 w - - 3 28",
            "Kf2",
            # Pin one of the attackers, but e2 pawn still hangs.
            # What should we do here? It's not saving value, but there are
            # fewer pieces hanging.
            ["Rb8"],
            False,
        ),
        (
            "5rk1/pRQ3pp/6r1/8/3nN3/P4PP1/q3P1KP/4R3 w - - 3 28",
            "Kf2",
            # check + block the sight of an attacker, but the moved piece hangs
            ["Nf6+"],
            False,
        ),
        (
            "5rk1/pRQ3pp/6r1/8/3nN3/P4PP1/q3P1KP/4R3 w - - 3 28",
            "Kf2",
            # the suggested move is to protect one of the pawns, but not both
            ["Kf1"],
            False,
        ),
        # Assorted example 4, pinned piece
        (
            "5rk1/R5pp/4r3/8/2n1N3/P4PP1/4PK1P/8 w - - 1 35",
            "a4",
            # best is to move the piece
            ["Ng5"],
            True,
        ),
        (
            "5rk1/R5pp/4r3/8/2n1N3/P4PP1/4PK1P/8 w - - 1 35",
            "a4",
            # best is to get out of pin
            ["Kg1"],
            True,
        ),
        # Assorted example 5 - this is hanging other piece
        # (e2 was not hanging before the move)
        (
            "5rk1/R5pp/8/8/P1n1r3/5PP1/4PK1P/8 w - - 0 36",
            "Kg2",
            ["Rd7"],
            False,
        ),
        # Assorted example 6 - best is to counter-attack (with check)
        (
            "r1b3k1/pp2q3/8/7p/3Np1p1/2QnP1BP/PP4P1/5RK1 w - - 2 24",
            "Bf4",
            ["Qb3+"],
            True,
        ),
        # Assorted example 7 - hanging piece could be captured with a check
        (
            "1r3rk1/p1p3pp/4p3/5p2/1b1P4/2N2q2/PP3P1P/R1B1KQR1 w Q - 4 17",
            "Qg2",
            ["Bd2"],
            True,
        ),
        # Assorted example 8 - best is to counter-attack
        pytest.param(
            "r3k2r/ppq1pp2/2n2bpp/1B1p4/3Pb3/1PP2N2/P2N1PPP/R2QR1K1 b kq - 2 13",
            "h5",
            ["a6"],
            True,
            marks=pytest.mark.xfail(),
        ),
        # you can save value by trading the hanging piece
        pytest.param(
            "r3k2r/ppq1pp2/2n2bpp/1B1p4/3Pb3/1PP2N2/P2N1PPP/R2QR1K1 b kq - 2 13",
            "h5",
            ["Bxf3"],
            True,
        ),
        # A piece was hanging before the move, then it's moved, but also
        # to a square where it can be captured. This case should be classified
        # as hang_moved_piece, not as left_piece_hangin.
        pytest.param(
            "r3k2r/1p3pb1/p1n1p1pp/3q4/3PnB2/N2Q1N1P/PP3PP1/2R1R1K1 b kq - 1 17",
            "Nc5",
            ["Ng5"],
            False,
        ),
    ],
)
def test_left_piece_hanging(fen, move_san, best_moves_san, expected):
    board, move, best_moves = _board_move_best_moves(fen, move_san, best_moves_san)
    if left_piece_hanging(board, move, best_moves) is not expected:
        print(board.fen())
        print(get_lichess_analyze_link(board.fen()))
        print(board)
        print(
            f"move={board.san(move)} best_moves={moves_to_san_list(board, best_moves)} {expected=}"
        )
        raise AssertionError()


def _board_move_best_moves(
    fen: str, move_san: str, best_moves_san: Optional[list[str]] = None
) -> tuple[chess.Board, chess.Move, list[chess.Move]]:
    board = chess.Board(fen)
    move = board.parse_san(move_san)
    if best_moves_san is None:
        best_moves = None
    else:
        best_moves = [board.parse_san(m) for m in best_moves_san]
    return board, move, best_moves


def _best_opponent_moves(
    board: chess.Board, move: chess.Move, best_opponent_moves_san: list[str]
) -> list[chess.Move]:
    board_after_move = board.copy()
    board_after_move.push(move)
    return [board_after_move.parse_san(m) for m in best_opponent_moves_san]


@pytest.mark.parametrize(
    ["score", "best_score", "n", "expected"],
    [
        # Mates in 1
        (Cp(-100), Cp(0), 1, False),
        (Mate(-1), Cp(0), 1, True),
        (Mate(-1), Mate(-1), 1, False),
        (Mate(-1), Mate(1), 1, True),
        (Mate(-1), Mate(-2), 1, True),
        (Mate(-2), Mate(-4), 1, False),
        (Mate(1), Cp(0), 1, False),
        # Mates in 2+
        (Mate(-2), Mate(-4), 2, True),
        (Mate(-2), Mate(-2), 2, False),
        (Mate(-1), Mate(-2), 2, False),
        (Mate(-1), Mate(2), 2, False),
        (Mate(-1), Mate(-3), 2, False),
        (Mate(-5), Cp(0), 5, True),
        (Mate(-4), Cp(0), 5, False),
        (Mate(-6), Cp(0), 5, False),
    ],
)
def test_hung_mate_n(score, best_score, n, expected):
    assert hung_mate_n(score, best_score, n) is expected


@pytest.mark.parametrize(
    ["score", "best_score", "n", "expected"],
    [
        # Mates in 1
        (Cp(-100), Cp(0), 1, False),
        (Mate(-1), Cp(0), 1, True),
        (Mate(-1), Mate(-1), 1, False),
        (Mate(-1), Mate(1), 1, True),
        (Mate(-1), Mate(-2), 1, False),
        (Mate(-2), Mate(-4), 1, False),
        # Mates in 3+
        (Mate(-2), Mate(-4), 3, False),
        (Mate(-2), Cp(0), 3, False),
        (Mate(-3), Cp(0), 3, True),
        (Mate(-10), Cp(0), 3, True),
    ],
)
def test_hung_mate_n_plus(score, best_score, n, expected):
    assert hung_mate_n_plus(score, best_score, n) is expected


@pytest.mark.parametrize(
    ["score", "best_score", "n", "expected"],
    [
        (Cp(100), Mate(1), 1, True),
        (Cp(100), Mate(2), 1, False),
        (Mate(2), Mate(2), 1, False),
        (Mate(2), Mate(1), 1, True),
        (Mate(-1), Mate(1), 1, True),
        (Mate(1), Mate(1), 1, False),
        (Mate(2), Mate(2), 2, False),
        (Mate(1), Mate(1), 2, False),
        (Mate(5), Mate(2), 2, True),
    ],
)
def test_missed_mate_n(score, best_score, n, expected):
    assert missed_mate_n(score, best_score, n) is expected


@pytest.mark.parametrize(
    ["score", "best_score", "n", "expected"],
    [
        (Cp(100), Mate(4), 2, True),
        (Cp(100), Mate(2), 2, True),
        (Cp(100), Mate(1), 2, False),
        (Mate(1), Mate(1), 2, False),
        (Mate(4), Mate(5), 2, False),
        (Mate(6), Mate(3), 2, False),
    ],
)
def test_missed_mane_n_plus(score, best_score, n, expected):
    assert missed_mate_n_plus(score, best_score, n) is expected


@pytest.mark.parametrize(
    ["fen", "move_san", "best_moves_san", "expected"],
    [
        # Assorted example 1
        (
            "1k5r/pbpr1p2/1p5p/n2pP3/3P4/2P2NPp/2Q2P1P/RR4K1 w - - 2 19",
            "Ra4",
            ["Rxa5"],
            True,
        ),
        (
            "1k5r/pbpr1p2/1p5p/n2pP3/3P4/2P2NPp/2Q2P1P/RR4K1 w - - 2 19",
            "Rxa5",
            ["Rxa5"],
            False,
        ),
        # Assorted example 2: setting up mate
        (
            "r1b2rk1/pp5p/4ppB1/4N1Qn/8/8/PP3PPP/3q1RK1 w - - 0 21",
            "Qxh5",
            ["Bxh7+"],
            True,
        ),
        # Assorted example 3: another mate
        (
            "2k3nr/pp1rpp1p/2pp2p1/4P3/1RP5/2PB1Q2/q4PPP/1R4K1 w - - 2 16",
            "Qxf7",
            ["Qxc6+"],
            True,
        ),
        # Assorted example 4: pawn is not protected because of tactics
        (
            "2kr3r/pp2pp2/2q2bp1/8/2PPR3/1P3NPp/P3QP1P/R5K1 b - - 0 19",
            "g5",
            ["Bxd4"],
            True,
        ),
        # Assorted example 5: not a real sacrifice because of a fork in the end
        (
            "r1bq1rk1/pp2bppp/2n1p3/1Bp1P3/3P4/P1P2N2/5PPP/R1BQK2R b KQ - 3 10",
            "Bd7",
            ["Nxd4"],
            True,
        ),
        # Assorted example 6: setting up a pin
        (
            "rnb2rk1/pp1q3p/4p1p1/4P1N1/3P4/3B4/P1Q2PP1/1R3RK1 w - - 0 20",
            "Bb5",
            ["Nxe6"],
            True,
        ),
        # Assorted example 7: greek gift
        (
            "rnbq1rk1/ppp2ppp/4p3/3nP3/1b1P4/2NB1N2/PP3PPP/R1BQK2R w KQ - 1 9",
            "Bd2",
            ["Bxh7+"],
            True,
        ),
        # Assorted example 8: trying to defend
        (
            "1r5r/p3kpp1/2Qbpn1p/3p1NB1/3P2P1/3q1N1P/PP3P2/4R1K1 b - - 1 22",
            "Kf8",
            ["Qxf5"],
            True,
        ),
        # Assorted example 9: this should be classified as a discovered
        # attack instead (not implemented)
        pytest.param(
            "r2qr1k1/pp1n1pbp/3p1np1/2pP1b2/1PP5/P1N2N2/4BPPP/R1BQR1K1 b - - 0 12",
            "b6",
            ["Nxd5"],
            False,
            marks=pytest.mark.xfail(
                reason="discovered attacks detection is not implemented"
            ),
        ),
        # Assorted example 10: another discovered attack
        pytest.param(
            "r4rk1/5p2/pqb2B1p/3p2p1/P1pP4/2P1P3/2B2PPP/3Q1RK1 b - - 0 19",
            "Qb2",
            ["Bxa4"],
            False,
            marks=pytest.mark.xfail(
                reason="discovered attacks detection is not implemented"
            ),
        ),
    ],
)
def test_missed_sacrifice(fen, move_san, best_moves_san, expected):
    board, move, best_moves = _board_move_best_moves(fen, move_san, best_moves_san)
    assert missed_sacrifice(board, move, best_moves) is expected
