#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import sys

from base_python.entrypoint import launch
from source_zoom_singer import SourceZoomSinger

if __name__ == "__main__":
    source = SourceZoomSinger()
    launch(source, sys.argv[1:])
