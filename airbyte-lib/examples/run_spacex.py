# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
from __future__ import annotations

from itertools import islice

import airbyte_lib as ab


# preparation (from airbyte-lib main folder):
#   python -m venv .venv-source-spacex-api
#   source .venv-source-spacex-api/bin/activate
#   pip install -e ../airbyte-integrations/connectors/source-spacex-api
# In separate terminal:
#   poetry run python examples/run_spacex.py

source = ab.get_source(
    "source-spacex-api",
    config={"id": "605b4b6aaa5433645e37d03f"},
    install_if_missing=True,
)
cache = ab.new_local_cache()

source.check()

source.set_streams(["launches", "rockets", "capsules"])

result = source.read(cache)

print(islice(source.get_records("capsules"), 10))

for name, records in result.cache.streams.items():
    print(f"Stream {name}: {len(list(records))} records")
