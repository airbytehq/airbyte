#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_finn2 import SourceFinn2

if __name__ == "__main__":
    source = SourceFinn2()
    launch(source, sys.argv[1:])
