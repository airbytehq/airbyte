#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_workday_raas import SourceWorkdayRaas

if __name__ == "__main__":
    source = SourceWorkdayRaas()
    launch(source, sys.argv[1:])
