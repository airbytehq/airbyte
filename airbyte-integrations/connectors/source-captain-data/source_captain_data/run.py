#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_captain_data import SourceCaptainData


def run():
    source = SourceCaptainData()
    launch(source, sys.argv[1:])
