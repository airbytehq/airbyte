#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_k6_cloud import SourceK6Cloud


def run():
    source = SourceK6Cloud()
    launch(source, sys.argv[1:])
