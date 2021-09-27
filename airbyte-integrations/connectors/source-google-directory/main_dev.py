#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import sys

from base_python.entrypoint import launch
from source_google_directory import SourceGoogleDirectory

if __name__ == "__main__":
    source = SourceGoogleDirectory()
    launch(source, sys.argv[1:])
