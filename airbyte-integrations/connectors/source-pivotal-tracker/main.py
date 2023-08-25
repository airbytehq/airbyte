#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_pivotal_tracker import SourcePivotalTracker

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourcePivotalTracker()
    launch(source, sys.argv[1:])
