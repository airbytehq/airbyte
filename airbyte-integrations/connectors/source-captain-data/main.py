#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_captain_data import SourceCaptainData

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceCaptainData()
    launch(source, sys.argv[1:])
