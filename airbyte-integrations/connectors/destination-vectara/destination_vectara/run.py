#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


import sys

from destination_vectara import DestinationVectara


def run() -> None:
    DestinationVectara().run(sys.argv[1:])


if __name__ == "__main__":
    run()
