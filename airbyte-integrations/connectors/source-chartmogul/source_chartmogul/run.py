#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_chartmogul import SourceChartmogul


def run():
    source = SourceChartmogul()
    launch(source, sys.argv[1:])
