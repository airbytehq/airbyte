# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import os
import sys

from destination_motherduck import DestinationMotherDuck


def run() -> None:
    # Resolve unset "HOME" variable and lack of access to '/nonexistent' path
    os.environ["HOME"] = "/airbyte"

    DestinationMotherDuck().run(sys.argv[1:])


if __name__ == "__main__":
    run()
