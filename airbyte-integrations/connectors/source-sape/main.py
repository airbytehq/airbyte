#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_sape import SourceSape

if __name__ == "__main__":
    source = SourceSape()
    launch(source, sys.argv[1:])
