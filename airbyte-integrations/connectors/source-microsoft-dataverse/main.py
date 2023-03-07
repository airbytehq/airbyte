#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_microsoft_dataverse import SourceMicrosoftDataverse

if __name__ == "__main__":
    source = SourceMicrosoftDataverse()
    launch(source, sys.argv[1:])
