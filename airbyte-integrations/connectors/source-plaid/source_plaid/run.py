#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_plaid import SourcePlaid


def run():
    source = SourcePlaid()
    launch(source, sys.argv[1:])
