#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_babelforce import SourceBabelforce

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceBabelforce()
    launch(source, sys.argv[1:])
