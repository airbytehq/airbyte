#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_launchdarkly import SourceLaunchdarkly

if __name__ == "__main__":
    source = SourceLaunchdarkly()
    launch(source, sys.argv[1:])
