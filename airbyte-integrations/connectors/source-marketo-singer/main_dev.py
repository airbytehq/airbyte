#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import sys

from base_python.entrypoint import launch
from source_marketo_singer import SourceMarketoSinger

if __name__ == "__main__":
    source = SourceMarketoSinger()
    launch(source, sys.argv[1:])
