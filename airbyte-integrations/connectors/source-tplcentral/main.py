#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_tplcentral import SourceTplcentral

if __name__ == "__main__":
    source = SourceTplcentral()
    launch(source, sys.argv[1:])
