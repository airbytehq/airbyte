#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from .source import SourceAstra

def run():
    source = SourceAstra()
    launch(source, sys.argv[1:])

if __name__ == "__main__":
    source = SourceAstra()
    launch(source, sys.argv[1:])
