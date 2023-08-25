#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_microsoft_dataverse import SourceMicrosoftDataverse

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceMicrosoftDataverse()
    launch(source, sys.argv[1:])
