"""Utility functions for index selection."""


def argmax(lst: list) -> int:
    """Return the index of the largest value in a list.

    Args:
        lst: Non-empty list of comparable values.

    Returns:
        Index of the first maximum value.

    Raises:
        ValueError: If the list is empty.
    """
    return max(range(len(lst)), key=lambda i: lst[i])


def argmin(lst: list) -> int:
    """Return the index of the smallest value in a list.

    Args:
        lst: Non-empty list of comparable values.

    Returns:
        Index of the first minimum value.

    Raises:
        ValueError: If the list is empty.
    """
    return min(range(len(lst)), key=lambda i: lst[i])
