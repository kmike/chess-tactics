def running_total(lst):
    """
    >>> running_total([])
    []

    >>> running_total([1])
    [1]

    >>> running_total([1, -2, 3, 4])
    [1, -1, 2, 6]
    """
    accum = 0
    out = []
    for x in lst:
        accum += x
        out.append(accum)
    return out
