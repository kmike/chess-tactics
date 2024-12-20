import chess
import pytest

from chess_tactics.exchange import (
    get_capture_exchange_evaluation,
    get_exchange_evaluation,
    get_move_captured_value,
)

from .fens import (
    CAPTURE_WITH_PROMOTION,
    EXAMPLE_00,
    EXAMPLE_01,
    EXAMPLE_02,
    EXAMPLE_03,
    EXAMPLE_04,
    EXAMPLE_05,
    NIMZOVICH_TARRASCH,
)

# test cases from
# https://github.com/lithander/Leorik/blob/1768b138531261dc65c378f909085d5c49bc056c/Leorik.Test/see.epd
LEORIK_TEST_EXAMPLES = [
    ("6k1/1pp4p/p1pb4/6q1/3P1pRr/2P4P/PP1Br1P1/5RKN w - - 0 1", "Rfxf4", -1),
    ("5rk1/1pp2q1p/p1pb4/8/3P1NP1/2P5/1P1BQ1P1/5RK1 b - - 0 1", "Bxf4", 0),
    ("4R3/2r3p1/5bk1/1p1r3p/p2PR1P1/P1BK1P2/1P6/8 b - - 0 1", "hxg4", 0),
    ("4R3/2r3p1/5bk1/1p1r1p1p/p2PR1P1/P1BK1P2/1P6/8 b - - 0 1", "hxg4", 0),
    ("4r1k1/5pp1/nbp4p/1p2p2q/1P2P1b1/1BP2N1P/1B2QPPK/3R4 b - - 0 1", "Bxf3", 0),
    ("2r1r1k1/pp1bppbp/3p1np1/q3P3/2P2P2/1P2B3/P1N1B1PP/2RQ1RK1 b - - 0 1", "dxe5", 1),
    ("7r/5qpk/p1Qp1b1p/3r3n/BB3p2/5p2/P1P2P2/4RK1R w - - 0 1", "Re8", 0),
    ("6rr/6pk/p1Qp1b1p/2n5/1B3p2/5p2/P1P2P2/4RK1R w - - 0 1", "Re8", -5),
    ("7r/5qpk/2Qp1b1p/1N1r3n/BB3p2/5p2/P1P2P2/4RK1R w - - 0 1", "Re8", -5),
    ("6RR/4bP2/8/8/5r2/3K4/5p2/4k3 w - - 0 1", "f8=Q", 2),
    ("6RR/4bP2/8/8/5r2/3K4/5p2/4k3 w - - 0 1", "f8=N", 2),
    pytest.param(
        "7R/5P2/8/8/6r1/3K4/5p2/4k3 w - - 0 1", "f8=Q", 8, marks=pytest.mark.xfail()
    ),  # pure promotion, without captures
    pytest.param(
        "7R/5P2/8/8/6r1/3K4/5p2/4k3 w - - 0 1", "f8=B", 2, marks=pytest.mark.xfail()
    ),  # pure promotion, without captures
    ("7R/4bP2/8/8/1q6/3K4/5p2/4k3 w - - 0 1", "f8=R", -1),  # promoted piece is hanging
    ("8/4kp2/2npp3/1Nn5/1p2PQP1/7q/1PP1B3/4KR1r b - - 0 1", "Rxf1+", 0),
    ("8/4kp2/2npp3/1Nn5/1p2P1P1/7q/1PP1B3/4KR1r b - - 0 1", "Rxf1+", 0),
    ("2r2r1k/6bp/p7/2q2p1Q/3PpP2/1B6/P5PP/2RR3K b - - 0 1", "Qxc1", 1),
    ("r2qk1nr/pp2ppbp/2b3p1/2p1p3/8/2N2N2/PPPP1PPP/R1BQR1K1 w kq - 0 1", "Nxe5", 1),
    (
        "6r1/4kq2/b2p1p2/p1pPb3/p1P2B1Q/2P4P/2B1R1P1/6K1 w - - 0 1",
        "Bxe5",
        1,
    ),  # a mistake in leorik's suite (was: 0)
    (
        "3q2nk/pb1r1p2/np6/3P2Pp/2p1P3/2R4B/PQ3P1P/3R2K1 w - h6 0 1",
        "gxh6",
        0,
    ),  # en passant!
    ("3q2nk/pb1r1p2/np6/3P2Pp/2p1P3/2R1B2B/PQ3P1P/3R2K1 w - h6 0 1", "gxh6", 1),
    ("2r4r/1P4pk/p2p1b1p/7n/BB3p2/2R2p2/P1P2P2/4RK2 w - - 0 1", "Rxc8", 5),
    pytest.param(
        "2r5/1P4pk/p2p1b1p/5b1n/BB3p2/2R2p2/P1P2P2/4RK2 w - - 0 1",
        "Rxc8",
        5,
        marks=pytest.mark.skip(),
    ),  # last capture is promotion; needs more analysis?
    ("2r4k/2r4p/p7/2b2p1b/4pP2/1BR5/P1R3PP/2Q4K w - - 0 1", "Rxc5", 3),
    ("8/pp6/2pkp3/4bp2/2R3b1/2P5/PP4B1/1K6 w - - 0 1", "Bxc6", -2),
    ("4q3/1p1pr1k1/1B2rp2/6p1/p3PP2/P3R1P1/1P2R1K1/4Q3 b - - 0 1", "Rxe4", -4),
    ("4q3/1p1pr1kb/1B2rp2/6p1/p3PP2/P3R1P1/1P2R1K1/4Q3 b - - 0 1", "Bxe4", 1),
    ("3r3k/3r4/2n1n3/8/3p4/2PR4/1B1Q4/3R3K w - - 0 1", "Rxd4", -1),
    ("1k1r4/1ppn3p/p4b2/4n3/8/P2N2P1/1PP1R1BP/2K1Q3 w - - 0 1", "Nxe5", 1),
    ("1k1r3q/1ppn3p/p4b2/4p3/8/P2N2P1/1PP1R1BP/2K1Q3 w - - 0 1", "Nxe5", -2),
    ("rnb2b1r/ppp2kpp/5n2/4P3/q2P3B/5R2/PPP2PPP/RN1QKB2 w Q - 0 1", "Bxf6", 1),
    ("r2q1rk1/2p1bppp/p2p1n2/1p2P3/4P1b1/1nP1BN2/PP3PPP/RN1QR1K1 b - - 0 1", "Bxf3", 0),
    ("r1bqkb1r/2pp1ppp/p1n5/1p2p3/3Pn3/1B3N2/PPP2PPP/RNBQ1RK1 b kq - 0 1", "Nxd4", 0),
    ("r1bq1r2/pp1ppkbp/4N1p1/n3P1B1/8/2N5/PPP2PPP/R2QK2R w KQ - 0 1", "Nxg7", 0),
    ("r1bq1r2/pp1ppkbp/4N1pB/n3P3/8/2N5/PPP2PPP/R2QK2R w KQ - 0 1", "Nxg7", 3),
    ("rnq1k2r/1b3ppp/p2bpn2/1p1p4/3N4/1BN1P3/PPP2PPP/R1BQR1K1 b kq - 0 1", "Bxh2", -2),
    ("rn2k2r/1bq2ppp/p2bpn2/1p1p4/3N4/1BN1P3/PPP2PPP/R1BQR1K1 b kq - 0 1", "Bxh2", 1),
    (
        "r2qkbn1/ppp1pp1p/3p1rp1/3Pn3/4P1b1/2N2N2/PPP2PPP/R1BQKB1R b KQq - 0 1",
        "Bxf3",
        1,
    ),
    ("rnbq1rk1/pppp1ppp/4pn2/8/1bPP4/P1N5/1PQ1PPPP/R1B1KBNR b KQ - 0 1", "Bxc3", 0),
    ("r4rk1/3nppbp/bq1p1np1/2pP4/8/2N2NPP/PP2PPB1/R1BQR1K1 b - - 0 1", "Qxb2", -8),
    ("r4rk1/1q1nppbp/b2p1np1/2pP4/8/2N2NPP/PP2PPB1/R1BQR1K1 b - - 0 1", "Nxd5", -2),
    ("1r3r2/5p2/4p2p/2k1n1P1/2PN1nP1/1P3P2/8/2KR1B1R b - - 0 1", "Rxb3", -4),
    ("1r3r2/5p2/4p2p/4n1P1/kPPN1nP1/5P2/8/2KR1B1R b - - 0 1", "Rxb4", 1),
    ("2r2rk1/5pp1/pp5p/q2p4/P3n3/1Q3NP1/1P2PP1P/2RR2K1 b - - 0 1", "Rxc1", 0),
    ("5rk1/5pp1/2r4p/5b2/2R5/6Q1/R1P1qPP1/5NK1 b - - 0 1", "Bxc2", -1),
    ("1r3r1k/p4pp1/2p1p2p/qpQP3P/2P5/3R4/PP3PP1/1K1R4 b - - 0 1", "Qxa2", -8),
    ("1r5k/p4pp1/2p1p2p/qpQP3P/2P2P2/1P1R4/P4rP1/1K1R4 b - - 0 1", "Qxa2", 1),
    (
        "r2q1rk1/1b2bppp/p2p1n2/1ppNp3/3nP3/P2P1N1P/BPP2PP1/R1BQR1K1 w - - 0 1",
        "Nxe7",
        0,
    ),
    ("rnbqrbn1/pp3ppp/3p4/2p2k2/4p3/3B1K2/PPP2PPP/RNB1Q1NR w - - 0 1", "Bxe4", 1),
    ("rnb1k2r/p3p1pp/1p3p1b/7n/1N2N3/3P1PB1/PPP1P1PP/R2QKB1R w KQkq - 0 1", "Nd6", -2),
    ("r1b1k2r/p4npp/1pp2p1b/7n/1N2N3/3P1PB1/PPP1P1PP/R2QKB1R w KQkq - 0 1", "Nd6", 0),
    ("2r1k2r/pb4pp/5p1b/2KB3n/4N3/2NP1PB1/PPP1P1PP/R2Q3R w k - 0 1", "Bc6", -3),
    ("2r1k2r/pb4pp/5p1b/2KB3n/1N2N3/3P1PB1/PPP1P1PP/R2Q3R w k - 0 1", "Bc6", 0),
    ("2r1k3/pbr3pp/5p1b/2KB3n/1N2N3/3P1PB1/PPP1P1PP/R2Q3R w - - 0 1", "Bc6", -3),
    pytest.param(
        "5k2/p2P2pp/8/1pb5/1Nn1P1n1/6Q1/PPP4P/R3K1NR w KQ - 0 1",
        "d8=Q",
        8,
        marks=pytest.mark.xfail(),
    ),  # pure promotion, without captures
    ("r4k2/p2P2pp/8/1pb5/1Nn1P1n1/6Q1/PPP4P/R3K1NR w KQ - 0 1", "d8=Q", -1),
    ("5k2/p2P2pp/1b6/1p6/1Nn1P1n1/8/PPP4P/R2QK1NR w KQ - 0 1", "d8=Q", 2),
    ("4kbnr/p1P1pppp/b7/4q3/7n/8/PP1PPPPP/RNBQKBNR w KQk - 0 1", "c8=Q", -1),
    ("4kbnr/p1P1pppp/b7/4q3/7n/8/PPQPPPPP/RNB1KBNR w KQk - 0 1", "c8=Q", 2),
    ("4kbnr/p1P1pppp/b7/4q3/7n/8/PPQPPPPP/RNB1KBNR w KQk - 0 1", "c8=Q", 2),
    ("4kbnr/p1P4p/b1q5/5pP1/4n3/5Q2/PP1PPP1P/RNB1KBNR w KQk f6 0 1", "gxf6", 0),
    ("4kbnr/p1P4p/b1q5/5pP1/4n3/5Q2/PP1PPP1P/RNB1KBNR w KQk f6 0 1", "gxf6", 0),
    ("4kbnr/p1P4p/b1q5/5pP1/4n2Q/8/PP1PPP1P/RNB1KBNR w KQk f6 0 1", "gxf6", 0),
    ("1n2kb1r/p1P4p/2qb4/5pP1/4n2Q/8/PP1PPP1P/RNB1KBNR w KQk - 0 1", "cxb8=Q", 2),
    ("rnbqk2r/pp3ppp/2p1pn2/3p4/3P4/N1P1BN2/PPB1PPPb/R2Q1RK1 w kq - 0 1", "Kxh2", 3),
    ("3N4/2K5/2n5/1k6/8/8/8/8 b - - 0 1", "Nxd8", 0),
    pytest.param(
        "3N4/2P5/2n5/1k6/8/8/8/4K3 b - - 0 1", "Nxd8", -8, marks=pytest.mark.xfail()
    ),  # last recapture is promotion
    pytest.param(
        "3n3r/2P5/8/1k6/8/8/3Q4/4K3 w - - 0 1", "Qxd8", 3, marks=pytest.mark.xfail()
    ),  # this one needs to be fixed
    ("3n3r/2P5/8/1k6/8/8/3Q4/4K3 w - - 0 1", "cxd8=Q", 7),
    ("r2n3r/2P1P3/4N3/1k6/8/8/8/4K3 w - - 0 1", "Nxd8", 3),
    ("8/8/8/1k6/6b1/4N3/2p3K1/3n4 w - - 0 1", "Nxd1", 0),
    pytest.param(
        "8/8/1k6/8/8/2N1N3/2p1p1K1/3n4 w - - 0 1", "Nexd1", -8, marks=pytest.mark.xfail
    ),  # needs to be fixed
    ("8/8/1k6/8/8/2N1N3/4p1K1/3n4 w - - 0 1", "Ncxd1", 1),
    ("r1bqk1nr/pppp1ppp/2n5/1B2p3/1b2P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 0 1", "O-O", 0),
]


@pytest.mark.parametrize(
    ["fen", "move", "expected_value"],
    [
        (EXAMPLE_00, "Bxe5", 1),  # pawn capture
        (EXAMPLE_00, "Bd4", -3),  # hang a bishop
        (EXAMPLE_01, "Bxe5", -2),  # B for a P
        (EXAMPLE_02, "Bxe5", 1),
        (EXAMPLE_03, "Bxe5", -2),
        (EXAMPLE_04, "Bxe5", 1),
        (EXAMPLE_04, "Rxe5", 1),
        (EXAMPLE_05, "Bxe5", -2),
        (EXAMPLE_05, "Rxe5", -2),
        (NIMZOVICH_TARRASCH, "Bxf1", 2),
        (NIMZOVICH_TARRASCH, "Qxf1", -2),
        (CAPTURE_WITH_PROMOTION, "dxe8=Q", 2),
    ],
)
def test_get_capture_exchange_evaluation(fen, move, expected_value):
    board = chess.Board(fen)
    if isinstance(move, str):
        move = board.parse_san(move)
    assert get_capture_exchange_evaluation(board, move) == expected_value


@pytest.mark.parametrize(
    ["fen", "move", "expected_value"],
    LEORIK_TEST_EXAMPLES,
)
def test_get_capture_exchange_evaluation_leorik(fen, move, expected_value):
    board = chess.Board(fen)
    move = board.parse_san(move)
    assert get_capture_exchange_evaluation(board, move) == expected_value


def test_get_exchange_evaluation_basic():
    board = chess.Board(NIMZOVICH_TARRASCH)
    assert get_exchange_evaluation(board, chess.BLACK, chess.F1) == 2
    assert get_exchange_evaluation(board, chess.BLACK, chess.E4) == 0


@pytest.mark.parametrize(
    ["fen", "move_san", "value"],
    [
        ("1k6/6b1/8/n3p1Pp/8/2B5/8/1K6 w - h6 0 1", "Bxe5", 1),
        ("1k6/6b1/8/n3p1Pp/8/2B5/8/1K6 w - h6 0 1", "Bxa5", 3),
        ("1k6/6b1/8/n3p1Pp/8/2B5/8/1K6 w - h6 0 1", "Bb4", 0),
        ("1k6/6b1/8/n3p1Pp/8/2B5/8/1K6 w - h6 0 1", "gxh6", 1),
    ],
)
def test_get_move_captured_value(fen, move_san, value):
    board = chess.Board(fen)
    move = board.parse_san(move_san)
    assert get_move_captured_value(board, move) == value
