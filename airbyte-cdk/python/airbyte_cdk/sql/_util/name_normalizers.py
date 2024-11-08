# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
"""Name normalizer classes."""

from __future__ import annotations

import abc
import functools
import re
from typing import TYPE_CHECKING

from airbyte_cdk.sql import exceptions as exc

if TYPE_CHECKING:
    from collections.abc import Iterable


class NameNormalizerBase(abc.ABC):
    """Abstract base class for name normalizers."""

    @staticmethod
    @abc.abstractmethod
    def normalize(name: str) -> str:
        """Return the normalized name."""
        ...

    @classmethod
    def normalize_set(cls, str_iter: Iterable[str]) -> set[str]:
        """Converts string iterable to a set of lower case strings."""
        return {cls.normalize(s) for s in str_iter}

    @classmethod
    def normalize_list(cls, str_iter: Iterable[str]) -> list[str]:
        """Converts string iterable to a list of lower case strings."""
        return [cls.normalize(s) for s in str_iter]

    @classmethod
    def check_matched(cls, name1: str, name2: str) -> bool:
        """Return True if the two names match after each is normalized."""
        return cls.normalize(name1) == cls.normalize(name2)

    @classmethod
    def check_normalized(cls, name: str) -> bool:
        """Return True if the name is already normalized."""
        return cls.normalize(name) == name


class LowerCaseNormalizer(NameNormalizerBase):
    """A name normalizer that converts names to lower case."""

    @staticmethod
    @functools.cache
    def normalize(name: str) -> str:
        """Return the normalized name.

        - All non-alphanumeric characters are replaced with underscores.
        - Any names that start with a numeric ("1", "2", "123", "1b" etc.) are prefixed
          with and underscore ("_1", "_2", "_123", "_1b" etc.)

        Examples:
        - "Hello World!" -> "hello_world"
        - "Hello, World!" -> "hello__world"
        - "Hello - World" -> "hello___world"
        - "___Hello, World___" -> "___hello__world___"
        - "Average Sales (%)" -> "average_sales____"
        - "Average Sales (#)" -> "average_sales____"
        - "+1" -> "_1"
        - "-1" -> "_1"
        """
        result = name

        # Replace all non-alphanumeric characters with underscores.
        result = re.sub("[^A-Za-z0-9]", "_", result.lower())

        # Check if name starts with a number and prepend "_" if it does.
        if result and result[0].isdigit():
            # Most databases do not allow identifiers to start with a number.
            result = f"_{result}"

        if not result.replace("_", ""):
            raise exc.AirbyteNameNormalizationError(
                message="Name cannot be empty after normalization.",
                raw_name=name,
                normalization_result=result,
            )

        return result


__all__ = [
    "NameNormalizerBase",
    "LowerCaseNormalizer",
]
