#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
"""Small internal tooling helper unrelated to any connector."""


def summarize_counts(counts: list[int]) -> int:
    total = 0
    for value in counts:
        total += value
    return total


if __name__ == "__main__":
    print(summarize_counts([1, 2, 3]))
