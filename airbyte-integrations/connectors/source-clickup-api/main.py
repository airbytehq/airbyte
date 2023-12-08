#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_clickup_api import SourceClickupApi

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceClickupApi()
    launch(source, sys.argv[1:])
