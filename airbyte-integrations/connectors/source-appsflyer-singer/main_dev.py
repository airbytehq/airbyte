#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import sys

from base_python.entrypoint import launch
from source_appsflyer_singer import SourceAppsflyerSinger

if __name__ == "__main__":
    source = SourceAppsflyerSinger()
    launch(source, sys.argv[1:])
