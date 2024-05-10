#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_auth0 import SourceAuth0


def run():
    source = SourceAuth0()
    launch(source, sys.argv[1:])
