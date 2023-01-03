#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_mailerlite import SourceMailerlite

if __name__ == "__main__":
    source = SourceMailerlite()
    launch(source, sys.argv[1:])
