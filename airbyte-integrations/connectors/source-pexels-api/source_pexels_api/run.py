#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_pexels_api import SourcePexelsApi


def run():
    source = SourcePexelsApi()
    launch(source, sys.argv[1:])
