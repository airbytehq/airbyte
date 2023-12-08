#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_k6_cloud import SourceK6Cloud

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceK6Cloud()
    launch(source, sys.argv[1:])
