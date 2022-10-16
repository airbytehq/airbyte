#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_close_com import SourceCloseCom

if __name__ == "__main__":
    source = SourceCloseCom()
    launch(source, sys.argv[1:])
