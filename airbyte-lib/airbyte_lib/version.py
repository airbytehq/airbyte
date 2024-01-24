# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
from __future__ import annotations

import importlib.metadata


airbyte_lib_version = importlib.metadata.version("airbyte-lib")


def get_version() -> str:
    return airbyte_lib_version
