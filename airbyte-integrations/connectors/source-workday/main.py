#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


import sys

from source_workday import SourceWorkday

from airbyte_cdk.entrypoint import launch


if __name__ == "__main__":
    source = SourceWorkday()
    launch(source, sys.argv[1:])
