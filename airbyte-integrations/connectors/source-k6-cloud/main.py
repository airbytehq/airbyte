#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_k6_cloud import SourceK6Cloud

if __name__ == "__main__":
    source = SourceK6Cloud()
    launch(source, sys.argv[1:])
