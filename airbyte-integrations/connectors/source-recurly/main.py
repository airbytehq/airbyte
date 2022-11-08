#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_recurly import SourceRecurly

if __name__ == "__main__":
    source = SourceRecurly()
    launch(source, sys.argv[1:])
