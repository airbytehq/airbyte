#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_doubleverify import SourceDoubleverify

if __name__ == "__main__":
    source = SourceDoubleverify()
    launch(source, sys.argv[1:])
