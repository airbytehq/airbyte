# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import os
import sys

from pathlib import Path

from destination_motherduck import DestinationMotherDuck


def run() -> None:
    # Resolve unset "HOME" variable and lack of access to '/nonexistent' path
    if "HOME" not in os.environ and Path("/airbyte").exists():
        os.environ["HOME"] = "/airbyte"

    DestinationMotherDuck().run(sys.argv[1:])


if __name__ == "__main__":
    run()
