#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_zenloop import SourceZenloop


def run():
    source = SourceZenloop()
    launch(source, sys.argv[1:])
