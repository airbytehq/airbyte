#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_notion import SourceNotion

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceNotion()
    launch(source, sys.argv[1:])
