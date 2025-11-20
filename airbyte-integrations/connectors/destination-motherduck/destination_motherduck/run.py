# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import os
import sys
from pathlib import Path


def run() -> None:
    if "HOME" not in os.environ:
        # Temporary fix for unset "HOME" variable leading to failure on '/nonexistent' path:
        # https://github.com/airbytehq/airbyte/issues/63710
        print("Warning: 'HOME' environment variable is not set.")
        if Path("/airbyte").exists():
            print("Found /airbyte directory. Setting as home.")
            os.environ["HOME"] = "/airbyte"
    elif os.environ["HOME"].strip() == "/nonexistent":
        print(f"Warning: 'HOME' env var is set to '{os.environ['HOME']}'.")
        if Path("/airbyte").exists():
            print("Found '/airbyte' directory. Setting as new 'HOME'.")
            os.environ["HOME"] = "/airbyte"
        else:
            print(f"No valid home directory found. Using default: '{os.environ['HOME']}'.")
    else:
        print(f"Using HOME: '{os.environ['HOME']}'")

    # Defer import to ensure env var is set prior to loading the DuckDB engine.
    from destination_motherduck import DestinationMotherDuck

    DestinationMotherDuck().run(sys.argv[1:])


if __name__ == "__main__":
    run()
