#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_files_abstract import SourceFilesAbstract

if __name__ == "__main__":
    source = SourceFilesAbstract()
    launch(source, sys.argv[1:])
