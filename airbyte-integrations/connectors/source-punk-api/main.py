#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_punk_api import SourcePunkApi

if __name__ == "__main__":
    source = SourcePunkApi()
    launch(source, sys.argv[1:])
