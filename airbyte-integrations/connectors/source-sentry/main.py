#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_sentry import SourceSentry

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceSentry()
    launch(source, sys.argv[1:])
