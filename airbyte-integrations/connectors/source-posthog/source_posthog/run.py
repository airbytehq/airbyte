#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_posthog import SourcePosthog


def run():
    source = SourcePosthog()
    launch(source, sys.argv[1:])
