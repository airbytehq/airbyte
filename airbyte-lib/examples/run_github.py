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


source = ab.get_connector("source-github")
source.set_config(
    {"repositories": ["airbytehq/airbyte"], "credentials": {"personal_access_token": GITHUB_TOKEN}}
)
source.check()
source.set_streams(["products", "users", "purchases"])

result = source.read()

for name, records in result.streams.items():
    print(f"Stream {name}: {len(records)} records")
