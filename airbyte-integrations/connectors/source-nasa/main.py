#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_nasa import SourceNasa

if __name__ == "__main__":
    source = SourceNasa()
    launch(source, sys.argv[1:])
