#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_punk_api import SourcePunkApi

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourcePunkApi()
    launch(source, sys.argv[1:])
