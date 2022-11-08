#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_intercom import SourceIntercom

if __name__ == "__main__":
    source = SourceIntercom()
    launch(source, sys.argv[1:])
