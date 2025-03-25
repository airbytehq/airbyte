# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


import sys

from destination_mariadb import DestinationMariaDB


def run() -> None:
    DestinationMariaDB().run(sys.argv[1:])


if __name__ == "__main__":
    run()
