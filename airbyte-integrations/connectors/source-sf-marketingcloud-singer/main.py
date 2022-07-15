#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import sys

from airbyte_cdk.entrypoint import launch
from source_sf_marketingcloud_singer import SourceSfMarketingcloudSinger

if __name__ == "__main__":
    source = SourceSfMarketingcloudSinger()
    launch(source, sys.argv[1:])
