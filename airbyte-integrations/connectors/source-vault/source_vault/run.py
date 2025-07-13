#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#
from __future__ import annotations

from source_vault import SourceVault


def run() -> None:
    SourceVault.launch()