# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
"""Internal utility functions for dealing with pip.

Note: This module is for internal use only and it should not be depended upon for production use.
It is subject to change without notice.
"""
from __future__ import annotations

from airbyte_lib._util.pip_util import connector_pip_url, github_pip_url


__all__ = [
    "connector_pip_url",
    "github_pip_url",
]
