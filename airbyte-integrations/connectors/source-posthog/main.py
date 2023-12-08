#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_posthog import SourcePosthog

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourcePosthog()
    launch(source, sys.argv[1:])
