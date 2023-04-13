#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_microvix import SourceMicrovix

if __name__ == "__main__":
    source = SourceMicrovix()
    launch(source, sys.argv[1:])
