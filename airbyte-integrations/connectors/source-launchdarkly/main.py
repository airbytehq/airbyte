#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_launchdarkly import SourceLaunchdarkly

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceLaunchdarkly()
    launch(source, sys.argv[1:])
