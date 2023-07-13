#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from destination_gympass import DestinationGympass

if __name__ == "__main__":
    DestinationGympass().run(sys.argv[1:])
