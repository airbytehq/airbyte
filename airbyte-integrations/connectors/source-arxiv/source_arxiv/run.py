#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import sys

from airbyte_cdk.entrypoint import launch
from source_arxiv import SourceArxiv


def run():
    source = SourceArxiv()
    launch(source, sys.argv[1:])
