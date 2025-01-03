from typing import Any


def format_coins(value) -> str:
    """
    Formats a numeric value into a human-readable format with suffixes.
    For example:
    - 17090000 -> 17.09M
    - 1000 -> 1.00K
    - 999 -> 999.00
    """
    if value >= 1e9:
        return f"{value / 1e9:.2f}B"
    elif value >= 1e6:
        return f"{value / 1e6:.2f}M"
    elif value >= 1e3:
        return f"{value / 1e3:.2f}K"
    else:
        return f"{value:.2f}"


def parse_coins(coins_str) -> float:
    """
    Parses a string with a suffix (k, M, B) into a numerical value.
    """
    multiplier = {"K": 1e3, "M": 1e6, "B": 1e9}
    if coins_str[-1] in multiplier:
        return float(coins_str[:-1]) * multiplier[coins_str[-1]]
    return float(coins_str)


def sort_column(tree, col, reverse) -> Any:
    """
    Sorts the Treeview by the specified column.
    Uses `parse_coins` for correctly sorting human-readable coin values.
    """

    def parse_value(value):
        try:
            # Attempt to parse coins if the column contains formatted coin values
            return parse_coins(value)
        except (ValueError, IndexError):
            # Fallback to original value for non-coin columns
            return value

    # Extract data and parse values for sorting
    data = [(parse_value(tree.set(k, col)), k) for k in tree.get_children("")]
    data.sort(key=lambda t: t[0], reverse=reverse)

    # Reorder the Treeview
    for index, (_, k) in enumerate(data):
        tree.move(k, "", index)

    # Update the column heading to toggle sorting direction
    tree.heading(col, command=lambda: sort_column(tree, col, not reverse))


def sortable_treeview(tree) -> None:
    """
    Enable runtime sorting for a Treeview.
    """
    for col in tree["columns"]:
        tree.heading(
            col, text=col, command=lambda _col=col: sort_column(tree, _col, False)
        )
