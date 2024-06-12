#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_recreation import SourceRecreation


def run():
    source = SourceRecreation()
    launch(source, sys.argv[1:])
