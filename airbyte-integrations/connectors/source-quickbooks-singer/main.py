#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_quickbooks_singer import SourceQuickbooksSinger

if __name__ == "__main__":
    source = SourceQuickbooksSinger()
    launch(source, sys.argv[1:])
