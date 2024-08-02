#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_clazar import SourceClazar

if __name__ == "__main__":
    source = SourceClazar()
    launch(source, sys.argv[1:])
