#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_expensify.source import SourceExpensify


def run():
    source = SourceExpensify()
    launch(source, sys.argv[1:])
