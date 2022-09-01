#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_fortnox import SourceFortnox

if __name__ == "__main__":
    source = SourceFortnox()
    launch(source, sys.argv[1:])
