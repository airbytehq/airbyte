#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_pivotal_tracker import SourcePivotalTracker

if __name__ == "__main__":
    source = SourcePivotalTracker()
    launch(source, sys.argv[1:])
