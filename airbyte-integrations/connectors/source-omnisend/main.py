#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_omnisend import SourceOmnisend

if __name__ == "__main__":
    source = SourceOmnisend()
    launch(source, sys.argv[1:])
