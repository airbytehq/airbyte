#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from destination_lamatic import DestinationLamatic

if __name__ == "__main__":
    DestinationLamatic().run(sys.argv[1:])
