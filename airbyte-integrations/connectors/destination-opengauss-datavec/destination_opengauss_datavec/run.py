# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#


import sys

from destination_opengauss_datavec import DestinationOpenGaussDataVec


def run() -> None:
    DestinationOpenGaussDataVec().run(sys.argv[1:])


if __name__ == "__main__":
    run()
