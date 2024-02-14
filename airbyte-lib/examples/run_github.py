# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
"""A simple test of AirbyteLib, using the Faker source connector.

Usage (from airbyte-lib root directory):
> poetry run python ./examples/run_github.py

No setup is needed, but you may need to delete the .venv-source-faker folder
if your installation gets interrupted or corrupted.
"""
from __future__ import annotations

import airbyte_lib as ab


# Create a token here: https://github.com/settings/tokens
GITHUB_TOKEN = ab.get_secret("GITHUB_PERSONAL_ACCESS_TOKEN")


source = ab.get_source("source-github")
source.set_config(
    {
        "repositories": ["airbytehq/quickstarts"],
        "credentials": {"personal_access_token": GITHUB_TOKEN},
    }
)
source.check()
source.select_streams(["issues", "pull_requests", "commits"])

result = source.read()

for name, records in result.streams.items():
    print(f"Stream {name}: {len(records)} records")
