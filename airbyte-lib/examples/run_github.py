# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
"""A simple test of AirbyteLib, using the Faker source connector.

Usage (from airbyte-lib root directory):
> poetry run python ./examples/run_faker.py

No setup is needed, but you may need to delete the .venv-source-faker folder
if your installation gets interrupted or corrupted.
"""
from __future__ import annotations

import airbyte_lib as ab


GITHUB_TOKEN = ab.get_secret("GITHUB_PERSONAL_ACCESS_TOKEN")


source = ab.get_source("source-github")
source.set_config(
    {"repositories": ["airbytehq/integration-test"], "credentials": {"personal_access_token": GITHUB_TOKEN}}
)
source.check()
source.set_streams(["issues"])

# for record in source.get_records("issues"):
#     print(record)

result = source.read(cache=ab.new_local_cache("github"))
print(result.processed_records)

# for name, records in result.streams.items():
#     print(f"Stream {name}: {len(records)} records")
