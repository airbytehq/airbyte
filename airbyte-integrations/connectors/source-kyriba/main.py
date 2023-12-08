#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_kyriba import SourceKyriba

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceKyriba()
    launch(source, sys.argv[1:])
