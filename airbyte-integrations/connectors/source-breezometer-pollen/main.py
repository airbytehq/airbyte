#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_breezometer_pollen import SourceBreezometerPollen

if __name__ == "__main__":
    source = SourceBreezometerPollen()
    launch(source, sys.argv[1:])
