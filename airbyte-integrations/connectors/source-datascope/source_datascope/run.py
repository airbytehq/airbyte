#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_datascope import SourceDatascope


def run():
    source = SourceDatascope()
    launch(source, sys.argv[1:])
