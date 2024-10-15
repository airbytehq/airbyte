# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
"""Support for PyAirbyte version checks."""

from __future__ import annotations

import importlib.metadata


airbyte_version = importlib.metadata.version("airbyte")


def get_version() -> str:
    """Return the version of PyAirbyte."""
    return airbyte_version
