#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_tidsbanken_api import SourceTidsbankenApi

if __name__ == "__main__":
    source = SourceTidsbankenApi()
    launch(source, sys.argv[1:])
