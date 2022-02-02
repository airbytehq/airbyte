#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_test_connector import SourceTestConnector

if __name__ == "__main__":
    source = SourceTestConnector()
    # make catalog not required for testing
    if(sys.argv.count("--catalog") == 0):
        sys.argv.append('--catalog')
        sys.argv.append('dummy.json')
    launch(source, sys.argv[1:])
