#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_my_hours import SourceMyHours

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceMyHours()
    launch(source, sys.argv[1:])
