#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from destination_scaffold_destination_python import DestinationScaffoldDestinationPython

if __name__ == "__main__":
    DestinationScaffoldDestinationPython().run(sys.argv[1:])
