#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from destination_opengauss_datavec import DestinationOpenGaussDataVec


if __name__ == "__main__":
    DestinationOpenGaussDataVec().run(sys.argv[1:])
