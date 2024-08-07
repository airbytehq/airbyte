#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_marketo import SourceMarketo


def run():
    source = SourceMarketo()
    launch(source, sys.argv[1:])
