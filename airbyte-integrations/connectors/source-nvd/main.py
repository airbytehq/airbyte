#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_nvd import SourceNvd

if __name__ == "__main__":
    source = SourceNvd()
    launch(source, sys.argv[1:])
