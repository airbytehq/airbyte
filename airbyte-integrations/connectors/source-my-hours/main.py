#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_my_hours import SourceMyHours

if __name__ == "__main__":
    source = SourceMyHours()
    launch(source, sys.argv[1:])
