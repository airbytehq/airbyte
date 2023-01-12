#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_databend import SourceDatabend

if __name__ == "__main__":
    source = SourceDatabend()
    launch(source, sys.argv[1:])
