#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_trello import SourceTrello


def run():
    source = SourceTrello()
    launch(source, sys.argv[1:])
