#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_clickup_api import SourceClickupApi


def run():
    source = SourceClickupApi()
    launch(source, sys.argv[1:])
