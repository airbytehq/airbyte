#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_microsoft_sharepoint import SourceMicrosoftSharePoint

if __name__ == "__main__":
    source = SourceMicrosoftSharePoint()
    launch(source, sys.argv[1:])
