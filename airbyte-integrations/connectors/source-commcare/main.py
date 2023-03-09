#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_commcare import SourceCommcare

if __name__ == "__main__":
    source = SourceCommcare()
    launch(source, sys.argv[1:])
