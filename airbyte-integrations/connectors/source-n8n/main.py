#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_n8n import SourceN8n

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceN8n()
    launch(source, sys.argv[1:])
