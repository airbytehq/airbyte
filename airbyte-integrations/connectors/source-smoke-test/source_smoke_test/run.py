#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import sys

from airbyte_cdk.entrypoint import launch
from source_smoke_test import SourceSmokeTest


def run():
    source = SourceSmokeTest()
    launch(source, sys.argv[1:])


if __name__ == "__main__":
    run()
