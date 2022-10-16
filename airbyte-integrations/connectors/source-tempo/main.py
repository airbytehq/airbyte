#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_tempo import SourceTempo

if __name__ == "__main__":
    source = SourceTempo()
    launch(source, sys.argv[1:])
