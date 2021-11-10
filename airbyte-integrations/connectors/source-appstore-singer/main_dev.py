#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import sys

from base_python.entrypoint import launch
from source_appstore_singer import SourceAppstoreSinger

if __name__ == "__main__":
    source = SourceAppstoreSinger()
    launch(source, sys.argv[1:])
