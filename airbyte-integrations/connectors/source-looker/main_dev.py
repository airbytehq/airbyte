#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import sys

from base_python.entrypoint import launch
from source_looker import SourceLooker

if __name__ == "__main__":
    source = SourceLooker()
    launch(source, sys.argv[1:])
