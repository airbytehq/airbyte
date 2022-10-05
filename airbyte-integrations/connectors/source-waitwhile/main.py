#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_waitwhile import SourceWaitwhile

if __name__ == "__main__":
    source = SourceWaitwhile()
    launch(source, sys.argv[1:])
