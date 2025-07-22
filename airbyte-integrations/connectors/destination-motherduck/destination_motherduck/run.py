# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import os
import sys

from pathlib import Path

from destination_motherduck import DestinationMotherDuck


def run() -> None:
    if "HOME" not in os.environ and Path("/airbyte").exists():
        # Temporary fix for unset "HOME" variable leading to failure on '/nonexistent' path:
        # https://github.com/airbytehq/airbyte/issues/63710
        os.environ["HOME"] = "/airbyte"

    DestinationMotherDuck().run(sys.argv[1:])


if __name__ == "__main__":
    run()
