#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_trustpilot import SourceTrustpilot


def run():
    source = SourceTrustpilot()
    launch(source, sys.argv[1:])
