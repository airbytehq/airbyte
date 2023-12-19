# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import airbyte_lib as ab

# poetry run python examples/run_spacex_docker.py

source = ab.get_connector("source-spacex-api", config={"id": "605b4b6aaa5433645e37d03f"}, use_docker=True)
cache = ab.get_in_memory_cache()

source.check()

source.set_streams(["launches", "rockets", "capsules"])

result = ab.sync(source, cache)

print(source.peek("capsules"))

for name, records in result.cache.streams.items():
    print(f"Stream {name}: {len(records)} records")
