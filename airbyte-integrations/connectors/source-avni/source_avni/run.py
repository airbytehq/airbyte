#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_avni import SourceAvni

from airbyte_cdk.entrypoint import launch


def run():
    source = SourceAvni()
    launch(source, sys.argv[1:])
