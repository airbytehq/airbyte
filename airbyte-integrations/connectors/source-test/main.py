#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_test import SourceTest

if __name__ == "__main__":
    source = SourceTest()
    launch(source, sys.argv[1:])
