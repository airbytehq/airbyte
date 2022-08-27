#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_graffle import SourceGraffle

if __name__ == "__main__":
    source = SourceGraffle()
    launch(source, sys.argv[1:])
