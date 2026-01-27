# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


import sys

from destination_snowflake_cortex import DestinationSnowflakeCortex


def run() -> None:
    DestinationSnowflakeCortex().run(sys.argv[1:])


if __name__ == "__main__":
    run()
