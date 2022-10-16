#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_lemlist import SourceLemlist

if __name__ == "__main__":
    source = SourceLemlist()
    launch(source, sys.argv[1:])
