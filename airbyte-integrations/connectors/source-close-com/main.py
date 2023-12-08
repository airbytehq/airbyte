#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_close_com import SourceCloseCom

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceCloseCom()
    launch(source, sys.argv[1:])
