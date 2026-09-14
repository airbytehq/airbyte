#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_tiktok_shop import SourceTiktokShop

if __name__ == "__main__":
    source = SourceTiktokShop()
    launch(source, sys.argv[1:])
