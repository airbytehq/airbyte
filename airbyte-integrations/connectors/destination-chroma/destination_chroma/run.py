# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
"""Connector `run.py` entrypoint for the destination.

This file exposes a `run()` entrypoint, which is used by the CLI entrypoint with the
same name as the connector.
"""
from __future__ import annotations

import sys

from destination_chroma import DestinationChroma


def run() -> None:
    DestinationChroma().run(sys.argv[1:])
