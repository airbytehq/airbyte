#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_mindbox import SourceMindbox

if __name__ == "__main__":
    source = SourceMindbox()
    launch(source, sys.argv[1:])
