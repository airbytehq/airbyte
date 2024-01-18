# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from itertools import islice

import airbyte_lib as ab
from airbyte_lib.caches import SnowflakeSQLCache, SnowflakeCacheConfig


source = ab.get_connector(
    "source-faker",
    config={"count": 10000, "seed": 0, "parallelism": 1, "always_updated": False},
    install_if_missing=True,
)
cache = SnowflakeSQLCache(SnowflakeCacheConfig(
    account="", # todo: Load from GSM
    username="",
    password="",
    database="",
    warehouse="",
))

source.check()

result = source.read(cache)

for name in ["products", "users", "purchases"]:
    print(f"Stream {name}: {len(list(result[name]))} records")
