# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import os

import airbyte_lib as ab

# preparation (from airbyte-lib main folder):
#   python -m venv .venv-source-test
#   source .venv-source-test/bin/activate
#   pip install -e ./tests/integration_tests/fixtures/source-test
# In separate terminal:
#   poetry run python examples/run_test_source.py

os.environ["AIRBYTE_LOCAL_REGISTRY"] = "./tests/integration_tests/fixtures/registry.json"

source = ab.get_connector("source-test", config={"apiKey": "test"})
cache = ab.get_in_memory_cache()

source.check()

print(source.get_available_streams())

result = source.read_all(cache)

print(result.processed_records)
print(list(result["stream1"]))
