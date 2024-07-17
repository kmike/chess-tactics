""" Some position useful in tests """

# examples with black pawn on E5 being attacked
EXAMPLE0 = "1k6/8/8/4p3/8/2B5/8/1K6 w - - 0 1"  # a pawn just hangs
EXAMPLE1 = "1k6/6b1/8/4p3/8/2B5/8/1K6 w - - 0 1"  # pawn is protected
EXAMPLE2 = "k7/6b1/8/4p3/8/2B5/1Q6/1K6 w - - 0 1"  # battery
EXAMPLE3 = "k6q/6b1/8/4p3/8/2B5/1Q6/1K6 w - - 0 1"  # 2 batteries
EXAMPLE4 = "k3r3/4q3/8/1R2p3/8/2B5/8/1K6 w - - 0 1"  # mixed pieces
EXAMPLE5 = "k7/4q3/4r3/1R2p3/8/2B5/8/1K6 w - - 0 1"  # the same as ex.4, but pieces are switched
EXAMPLE6 = "1n6/1r6/8/k3p3/8/8/1Q6/1K6 w - - 0 1"  # attacking Q is pinned
EXAMPLE7 = (
    "1k6/1r6/8/4p3/8/2B5/8/1K6 w - - 0 1"  # a pawn hangs, but the king is in check
)
EXAMPLE8 = "1k6/1r6/8/8/8/8/2p5/1K6 w - - 0 1"  # checked king can escape the check by taking a pawn
EXAMPLE8_1 = (
    "1k6/1r6/8/8/4B3/8/2p5/1K6 w - - 0 1"  # the same as ex.8, but B also attacks
)
EXAMPLE9 = (
    "1k6/2r5/8/8/4B3/8/2p5/1K6 w - - 0 1"  # check can be avoided by taking a pawn
)

# other examples
ILLEGAL_KING_ATTACK = "8/8/6k1/4q3/Q1Kb4/8/8/8 w - - 0 1"

# examples from games
NIMZOVICH_TARRASCH = "3rr1k1/p4p1p/6p1/2p5/3PN3/1P3P2/PBQ2Kb1/2R2R1q b - - 4 24"
