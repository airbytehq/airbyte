# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
"""Support for Airbyte version checks."""

from __future__ import annotations

import importlib.metadata


airbyte_version = importlib.metadata.version("airbyte_cdk")


def get_version() -> str:
    """Return the version of Airbyte."""
    return airbyte_version
