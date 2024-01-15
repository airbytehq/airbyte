# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from itertools import islice

import airbyte_lib as ab


source = ab.get_connector(
    "source-faker",
    config={"count": 10000, "seed": 0, "parallelism": 1, "always_updated": False},
    install_if_missing=True,
)
cache = ab.new_local_cache()

source.check()

# TODO: Pur the real stream names here:
streams = ["stream1", "stream2", "stream3"]
# source.set_streams(["launches", "rockets", "capsules"])

result = source.read(cache)

print(islice(source.get_records(streams[0]), 10))

for name, records in result.cache.streams.items():
    print(f"Stream {name}: {len(list(records))} records")
