#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_retently import SourceRetently


def run():
    source = SourceRetently()
    launch(source, sys.argv[1:])
