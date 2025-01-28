#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


import sys

from .source import SourceZohoCrm

from airbyte_cdk.entrypoint import launch


def run():
    source = SourceZohoCrm()
    launch(source, sys.argv[1:])
