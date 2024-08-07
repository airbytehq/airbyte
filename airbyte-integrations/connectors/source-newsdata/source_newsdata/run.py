#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_newsdata import SourceNewsdata


def run():
    source = SourceNewsdata()
    launch(source, sys.argv[1:])
