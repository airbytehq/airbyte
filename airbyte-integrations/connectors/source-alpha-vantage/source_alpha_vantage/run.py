#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_alpha_vantage import SourceAlphaVantage

from airbyte_cdk.entrypoint import launch


def run():
    source = SourceAlphaVantage()
    launch(source, sys.argv[1:])
