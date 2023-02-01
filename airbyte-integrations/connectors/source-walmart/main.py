#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_walmart import SourceWalmart

if __name__ == "__main__":
    source = SourceWalmart()
    launch(source, sys.argv[1:])
