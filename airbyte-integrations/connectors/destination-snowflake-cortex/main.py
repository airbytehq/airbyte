#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


import sys

from destination_snowflake_cortex import DestinationSnowflakeCortex

if __name__ == "__main__":
    DestinationSnowflakeCortex().run(sys.argv[1:])
