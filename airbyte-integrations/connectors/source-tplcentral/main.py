#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_tplcentral import SourceTplcentral

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceTplcentral()
    launch(source, sys.argv[1:])
