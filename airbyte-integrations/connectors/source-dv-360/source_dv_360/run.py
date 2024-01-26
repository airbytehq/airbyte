#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_dv_360 import SourceDV360


def run():
    source = SourceDV360()
    launch(source, sys.argv[1:])
