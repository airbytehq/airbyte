# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import os
import sys
from pathlib import Path

from destination_motherduck import DestinationMotherDuck


def run() -> None:
    if "HOME" not in os.environ:
        # Temporary fix for unset "HOME" variable leading to failure on '/nonexistent' path:
        # https://github.com/airbytehq/airbyte/issues/63710
        print("Warning: 'HOME' environment variable is not set.", file=sys.stderr)
        if Path("/airbyte").exists():
            print("Found /airbyte directory. Setting as home.", file=sys.stderr)
            os.environ["HOME"] = "/airbyte"
    else:
        print("Using HOME:", os.environ["HOME"], file=sys.stderr)

    DestinationMotherDuck().run(sys.argv[1:])


if __name__ == "__main__":
    run()
