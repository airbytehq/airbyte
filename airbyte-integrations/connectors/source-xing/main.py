#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_xing import SourceXing

if __name__ == "__main__":
    source = SourceXing()
    launch(source, sys.argv[1:])
