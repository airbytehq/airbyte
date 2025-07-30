#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from destination_opengauss_datavec import DestinationOpengaussDatavec


if __name__ == "__main__":
    DestinationOpengaussDatavec().run(sys.argv[1:])
