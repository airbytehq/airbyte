#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_recharge import SourceRecharge


def run():
    source = SourceRecharge()
    launch(source, sys.argv[1:])
