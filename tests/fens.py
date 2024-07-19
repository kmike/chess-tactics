""" Some position useful in tests """

# examples with black pawn on E5 being attacked
EXAMPLE_00 = "1k6/8/8/4p3/8/2B5/8/1K6 w - - 0 1"  # a pawn just hangs
EXAMPLE_01 = "1k6/6b1/8/4p3/8/2B5/8/1K6 w - - 0 1"  # pawn is protected
EXAMPLE_02 = "k7/6b1/8/4p3/8/2B5/1Q6/1K6 w - - 0 1"  # battery
EXAMPLE_03 = "k6q/6b1/8/4p3/8/2B5/1Q6/1K6 w - - 0 1"  # 2 batteries
EXAMPLE_04 = "k3r3/4q3/8/1R2p3/8/2B5/8/1K6 w - - 0 1"  # mixed pieces
EXAMPLE_05 = "k7/4q3/4r3/1R2p3/8/2B5/8/1K6 w - - 0 1"  # the same as ex.4, but pieces are switched
EXAMPLE_06 = "1n6/1r6/8/k3p3/8/8/1Q6/1K6 w - - 0 1"  # attacking Q is pinned
EXAMPLE_07 = (
    "1k6/1r6/8/4p3/8/2B5/8/1K6 w - - 0 1"  # a pawn hangs, but the king is in check
)
EXAMPLE_08 = "1k6/1r6/8/8/8/8/2p5/1K6 w - - 0 1"  # checked king can escape the check by taking a pawn
EXAMPLE_08_1 = (
    "1k6/1r6/8/8/4B3/8/2p5/1K6 w - - 0 1"  # the same as ex.8, but B also attacks
)
EXAMPLE_09 = (
    "1k6/2r5/8/8/4B3/8/2p5/1K6 w - - 0 1"  # check can be avoided by taking a pawn
)

# Examples with capturable / not capturable pieces on f6
EXAMPLE_10 = "8/1k6/5n2/8/4N3/8/1K6/8 w - - 0 1"  # hanging knights
EXAMPLE_11 = "8/1k4p1/5n2/8/4N3/8/1K6/8 w - - 0 1"  # knight which can be exchanged
EXAMPLE_12 = "8/1k6/5n2/8/8/3N4/1K6/8 w - - 0 1"  # nothing is hanging
EXAMPLE_13 = (
    "8/1k4p1/5n2/8/8/8/1K3R2/8 w - - 0 1"  # protected knight is attacked by a rook
)
EXAMPLE_14 = "8/1k2p1p1/5n2/3N4/8/8/1K3R2/8 w - - 0 1"  # well-ptotected knight

# fork examples
FORK_01 = "k7/8/1q3r2/3N4/8/8/2K5/8 w - - 0 1"  # a simple fork
FORK_02 = "k7/3r4/1q3r2/3N4/8/8/2K5/8 w - - 0 1"  # knight is hanging, not a fork
FORK_03 = "k7/4n3/1q6/3N4/8/8/2K5/8 w - - 0 1"  # knight tries to fork a knight
FORK_04 = "k7/3r4/1q3r2/3N4/4P3/8/2K5/8 w - - 0 1"  # like ex.2, but N is protected
FORK_05 = "k7/1b6/1q3r2/3N4/4P3/8/2K5/8 w - - 0 1"  # like ex.4, but N can be exchanged
FORK_06 = "1k6/8/8/8/1q1R2n1/8/1R6/1K6 w - - 0 1"  # forking a pinned piece
FORK_07 = (
    "2k5/8/8/8/1q1R2n1/8/1R6/1K6 w - - 0 1"  # the same as ex.6, but Q is not pinned
)
FORK_08 = (
    "1k6/8/8/7p/1q1R2n1/8/1R6/1K6 w - - 0 1"  # the same as ex.6, but N is protected
)
FORK_09 = "1k6/6p1/1p3r2/2q5/4N3/8/8/1K6 w - - 0 1"  # K attacks protected Q and R
FORK_10 = "1k6/6p1/1p3b2/2q5/4N3/8/8/1K6 w - - 0 1"  # K attacks protected Q and B
FORK_11 = "1k6/6p1/1p3b2/2q5/4N3/8/8/1K3R2 w - - 0 1"  # K attackes protected Q and B, but B is attacked twice
FORK_12 = (
    "4k3/3B1p2/4p3/8/Q7/8/8/4K3 w HAha - 2 14"  # king is involved (not a fork by B)
)
FORK_13 = "4k3/8/2B5/5p2/4p3/8/2Q5/4K3 w HAha - 2 14"  # similar to ex.12, but B is further from K
FORK_14 = "4k3/1p6/2B5/5p2/4p3/8/2Q5/4K3 w HAha - 2 14"  # fork with K in check and attacker hanging

# other examples
ILLEGAL_KING_ATTACK = "8/8/6k1/4q3/Q1Kb4/8/8/8 w - - 0 1"
CAPTURE_WITH_PROMOTION = (
    "4n2r/1k1P4/8/8/8/8/1K6/8 w - - 0 1"  # P captures N with promotion
)

# examples from games
NIMZOVICH_TARRASCH = "3rr1k1/p4p1p/6p1/2p5/3PN3/1P3P2/PBQ2Kb1/2R2R1q b - - 4 24"
