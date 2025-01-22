#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


import sys

from source_falcon import SourceFalcon

from airbyte_cdk.entrypoint import launch


if __name__ == "__main__":
    source = SourceFalcon()
    launch(source, sys.argv[1:])
