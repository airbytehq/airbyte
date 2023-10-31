from enum import Enum
from typing import Literal, TypedDict


REGION_TO_URL_MAPPING = {
    "Asia, Africa, and Latin America": "https://ads-dra.cloud.huawei.com/",
    "Russia": "https://ads-drru.cloud.huawei.ru/",
    "Europe": "https://ads-dre.cloud.huawei.com/",
}

STAT_TIME_GRANULARITY_MAPPING = {
    "Hourly": "STAT_TIME_GRANULARITY_HOURLY",
    "Daily": "STAT_TIME_GRANULARITY_DAILY",
    "Monthly": "STAT_TIME_GRANULARITY_MONTHLY",
}

StatTimeGranularity = Literal["Hourly", "Daily", "Monthly"]
Region = Literal["Asia, Africa, and Latin America", "Russia", "Europe"]
