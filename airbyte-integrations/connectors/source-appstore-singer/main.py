#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_appstore_singer import SourceAppstoreSinger

if __name__ == "__main__":
    source = SourceAppstoreSinger()
    launch(source, sys.argv[1:])
