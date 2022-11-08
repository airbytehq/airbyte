#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_posthog import SourcePosthog

if __name__ == "__main__":
    source = SourcePosthog()
    launch(source, sys.argv[1:])
