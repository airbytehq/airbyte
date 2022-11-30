#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_n8n import SourceN8n

if __name__ == "__main__":
    source = SourceN8n()
    launch(source, sys.argv[1:])
