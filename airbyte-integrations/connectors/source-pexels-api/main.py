#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_pexels_api import SourcePexelsApi

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourcePexelsApi()
    launch(source, sys.argv[1:])
