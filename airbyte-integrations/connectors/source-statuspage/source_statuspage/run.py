#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_statuspage import SourceStatuspage


def run():
    source = SourceStatuspage()
    launch(source, sys.argv[1:])
