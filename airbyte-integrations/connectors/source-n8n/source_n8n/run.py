#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_n8n import SourceN8n


def run():
    source = SourceN8n()
    launch(source, sys.argv[1:])
