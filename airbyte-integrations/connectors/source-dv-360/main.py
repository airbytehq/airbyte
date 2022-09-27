#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_dv_360 import SourceDV360

if __name__ == "__main__":
    source = SourceDV360()
    launch(source, sys.argv[1:])
