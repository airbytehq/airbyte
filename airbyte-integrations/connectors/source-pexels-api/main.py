#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_pexels_api import SourcePexelsApi

if __name__ == "__main__":
    source = SourcePexelsApi()
    launch(source, sys.argv[1:])
