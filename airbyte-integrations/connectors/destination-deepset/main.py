#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#
from __future__ import annotations

import sys

from destination_deepset import DestinationDeepset


if __name__ == "__main__":
    DestinationDeepset().run(sys.argv[1:])
