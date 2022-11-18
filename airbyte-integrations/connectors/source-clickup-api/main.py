#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_clickup_api import SourceClickupApi

if __name__ == "__main__":
    source = SourceClickupApi()
    launch(source, sys.argv[1:])
