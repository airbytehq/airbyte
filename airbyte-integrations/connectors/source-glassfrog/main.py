#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_glassfrog import SourceGlassfrog

if __name__ == "__main__":
    source = SourceGlassfrog()
    launch(source, sys.argv[1:])
