#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_launchdarkly import SourceLaunchdarkly


def run():
    source = SourceLaunchdarkly()
    launch(source, sys.argv[1:])
