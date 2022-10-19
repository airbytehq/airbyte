#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_timely import SourceTimely

if __name__ == "__main__":
    source = SourceTimely()
    launch(source, sys.argv[1:])
