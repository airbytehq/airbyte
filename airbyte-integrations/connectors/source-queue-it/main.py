#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_queue_it import SourceQueueIt

if __name__ == "__main__":
    source = SourceQueueIt()
    launch(source, sys.argv[1:])
