#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_datadog import SourceDatadog

if __name__ == "__main__":
    source = SourceDatadog()
    launch(source, sys.argv[1:])
