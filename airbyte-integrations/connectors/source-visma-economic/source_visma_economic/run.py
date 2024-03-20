#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_visma_economic import SourceVismaEconomic


def run():
    source = SourceVismaEconomic()
    launch(source, sys.argv[1:])
