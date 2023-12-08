#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_dv_360 import SourceDV360

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceDV360()
    launch(source, sys.argv[1:])
