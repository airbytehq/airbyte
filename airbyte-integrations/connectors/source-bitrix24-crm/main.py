#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_bitrix24_crm import SourceBitrix24Crm

if __name__ == "__main__":
    source = SourceBitrix24Crm()
    launch(source, sys.argv[1:])
