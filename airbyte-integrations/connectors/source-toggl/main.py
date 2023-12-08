#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_toggl import SourceToggl

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceToggl()
    launch(source, sys.argv[1:])
