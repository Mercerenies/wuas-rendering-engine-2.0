
"""Helper functions useful throughout the program."""


def lerp(a: float, b: float, amount: float) -> float:
    """Linear interpolation between a and b, using amount as the
    interpolation factor. If amount is not between 0 and 1, then this
    function extrapolateslinearly."""
    return a * (1 - amount) + b * amount
