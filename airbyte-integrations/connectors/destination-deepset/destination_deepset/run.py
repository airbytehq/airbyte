#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#
from __future__ import annotations

import sys

from .destination import DestinationDeepset


def run() -> None:
    destination = DestinationDeepset()
    destination.run(sys.argv[1:])
