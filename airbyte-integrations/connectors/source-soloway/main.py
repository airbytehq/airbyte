#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_soloway import SourceSoloway

if __name__ == "__main__":
    source = SourceSoloway()
    launch(source, sys.argv[1:])
