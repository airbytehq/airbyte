# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
from __future__ import annotations

import os

import airbyte_lib as ab


# preparation (from airbyte-lib main folder):
#   python -m venv .venv-source-test
#   source .venv-source-test/bin/activate
#   pip install -e ./tests/integration_tests/fixtures/source-test
# In separate terminal:
#   poetry run python examples/run_test_source.py

os.environ["AIRBYTE_LOCAL_REGISTRY"] = "./tests/integration_tests/fixtures/registry.json"

source = ab.get_source("source-test", config={"apiKey": "test"})
cache = ab.new_local_cache("cache_test")

source.check()

print(source.get_available_streams())

result = source.read(cache)

print(result.processed_records)
print(list(result["stream1"]))

different_cache = ab.new_local_cache("cache_test")
print(list(different_cache["stream1"]))
