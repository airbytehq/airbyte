#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_babelforce import SourceBabelforce

if __name__ == "__main__":
    source = SourceBabelforce()
    launch(source, sys.argv[1:])
