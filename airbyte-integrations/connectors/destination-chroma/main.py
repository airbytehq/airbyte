# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
"""Legacy `main.py` entrypoint for the destination.

This file is replaced by the `run.py` entrypoint and the CLI entrypoint with the same name
as the connector.
"""
from __future__ import annotations

from destination_chroma import run


if __name__ == "__main__":
    run.run()
