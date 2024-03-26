#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_drift import SourceDrift


def run():
    source = SourceDrift()
    launch(source, sys.argv[1:])
