#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from enum import Enum


class AmazonAdsRegion(str, Enum):
    NA = "NA"
    EU = "EU"
    FE = "FE"


URL_MAPPING = {
    "NA": "https://advertising-api.amazon.com/",
    "EU": "https://advertising-api-eu.amazon.com/",
    "FE": "https://advertising-api-fe.amazon.com/",
}
