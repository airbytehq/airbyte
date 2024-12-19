#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from destination_vectara import DestinationVectara

if __name__ == "__main__":
    DestinationVectara().run(sys.argv[1:])
