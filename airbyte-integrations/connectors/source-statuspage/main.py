#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_statuspage import SourceStatuspage

if __name__ == "__main__":
    source = SourceStatuspage()
    launch(source, sys.argv[1:])
