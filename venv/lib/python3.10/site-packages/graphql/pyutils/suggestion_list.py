from typing import Collection, Optional, List

from .natural_compare import natural_comparison_key

__all__ = ["suggestion_list"]


def suggestion_list(input_: str, options: Collection[str]) -> List[str]:
    """Get list with suggestions for a given input.

    Given an invalid input string and list of valid options, returns a filtered list
    of valid options sorted based on their similarity with the input.
    """
    options_by_distance = {}
    lexical_distance = LexicalDistance(input_)

    threshold = int(len(input_) * 0.4) + 1
    for option in options:
        distance = lexical_distance.measure(option, threshold)
        if distance is not None:
            options_by_distance[option] = distance

    # noinspection PyShadowingNames
    return sorted(
        options_by_distance,
        key=lambda option: (
            options_by_distance.get(option, 0),
            natural_comparison_key(option),
        ),
    )


class LexicalDistance:
    """Computes the lexical distance between strings A and B.

    The "distance" between two strings is given by counting the minimum number of edits
    needed to transform string A into string B. An edit can be an insertion, deletion,
    or substitution of a single character, or a swap of two adjacent characters.

    This distance can be useful for detecting typos in input or sorting.
    """

    _input: str
    _input_lower_case: str
    _input_list: List[int]
    _rows: List[List[int]]

    def __init__(self, input_: str):
        self._input = input_
        self._input_lower_case = input_.lower()
        row_size = len(input_) + 1
        self._input_list = list(map(ord, self._input_lower_case))

        self._rows = [[0] * row_size, [0] * row_size, [0] * row_size]

    def measure(self, option: str, threshold: int) -> Optional[int]:
        if self._input == option:
            return 0

        option_lower_case = option.lower()

        # Any case change counts as a single edit
        if self._input_lower_case == option_lower_case:
            return 1

        a, b = list(map(ord, option_lower_case)), self._input_list
        a_len, b_len = len(a), len(b)
        if a_len < b_len:
            a, b = b, a
            a_len, b_len = b_len, a_len

        if a_len - b_len > threshold:
            return None

        rows = self._rows
        for j in range(b_len + 1):
            rows[0][j] = j

        for i in range(1, a_len + 1):
            up_row = rows[(i - 1) % 3]
            current_row = rows[i % 3]

            smallest_cell = current_row[0] = i
            for j in range(1, b_len + 1):
                cost = 0 if a[i - 1] == b[j - 1] else 1

                current_cell = min(
                    up_row[j] + 1,  # delete
                    current_row[j - 1] + 1,  # insert
                    up_row[j - 1] + cost,  # substitute
                )

                if i > 1 and j > 1 and a[i - 1] == b[j - 2] and a[i - 2] == b[j - 1]:
                    # transposition
                    double_diagonal_cell = rows[(i - 2) % 3][j - 2]
                    current_cell = min(current_cell, double_diagonal_cell + 1)

                if current_cell < smallest_cell:
                    smallest_cell = current_cell

                current_row[j] = current_cell

            # Early exit, since distance can't go smaller than smallest element
            # of the previous row.
            if smallest_cell > threshold:
                return None

        distance = rows[a_len % 3][b_len]
        return distance if distance <= threshold else None
