#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import sys

from base_python.entrypoint import launch
from source_greenhouse import SourceGreenhouse

if __name__ == "__main__":
    source = SourceGreenhouse()
    launch(source, sys.argv[1:])
