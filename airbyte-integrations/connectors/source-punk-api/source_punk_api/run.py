#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_punk_api import SourcePunkApi


def run():
    source = SourcePunkApi()
    launch(source, sys.argv[1:])
