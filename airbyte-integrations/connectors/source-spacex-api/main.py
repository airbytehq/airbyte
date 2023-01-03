#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_spacex_api import SourceSpacexApi

if __name__ == "__main__":
    source = SourceSpacexApi()
    launch(source, sys.argv[1:])
