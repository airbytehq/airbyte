#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_coin_api import SourceCoinApi


def run():
    source = SourceCoinApi()
    launch(source, sys.argv[1:])
