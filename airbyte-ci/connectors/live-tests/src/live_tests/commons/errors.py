# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
from __future__ import annotations


class ExportError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
