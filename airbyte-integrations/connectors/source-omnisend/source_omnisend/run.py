#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_omnisend import SourceOmnisend


def run():
    source = SourceOmnisend()
    launch(source, sys.argv[1:])
