#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_quickbooks import SourceQuickbooks

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceQuickbooks()
    launch(source, sys.argv[1:])
