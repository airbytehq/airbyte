#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_sentry import SourceSentry


def run():
    source = SourceSentry()
    launch(source, sys.argv[1:])
