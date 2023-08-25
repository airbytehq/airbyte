#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_commcare import SourceCommcare

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceCommcare()
    launch(source, sys.argv[1:])
