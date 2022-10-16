#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_marketo import SourceMarketo

if __name__ == "__main__":
    source = SourceMarketo()
    launch(source, sys.argv[1:])
