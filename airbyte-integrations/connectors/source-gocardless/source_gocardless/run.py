#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_gocardless import SourceGocardless


def run():
    source = SourceGocardless()
    launch(source, sys.argv[1:])
