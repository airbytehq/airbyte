#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_calltouch import SourceCalltouch

if __name__ == "__main__":
    source = SourceCalltouch()
    launch(source, sys.argv[1:])
