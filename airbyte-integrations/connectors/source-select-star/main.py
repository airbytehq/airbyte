#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_select_star import SourceSelectStar

if __name__ == "__main__":
    source = SourceSelectStar()
    launch(source, sys.argv[1:])
