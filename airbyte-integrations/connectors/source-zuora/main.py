#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_zuora import SourceZuora

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceZuora()
    launch(source, sys.argv[1:])
