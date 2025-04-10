#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#


import sys

from destination_ragie import DestinationRagie

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "write":
        sys.stdin = open("./secrets/input_messages.txt", "r")

    DestinationRagie().run(sys.argv[1:])

