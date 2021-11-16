#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_snipeit import SourceSnipeit

if __name__ == "__main__":
    source = SourceSnipeit()
    launch(source, sys.argv[1:])
