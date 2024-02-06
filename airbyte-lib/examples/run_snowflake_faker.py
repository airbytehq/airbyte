# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
from __future__ import annotations

import json
import os

from google.cloud import secretmanager

import airbyte_lib as ab
from airbyte_lib.caches import SnowflakeCacheConfig, SnowflakeSQLCache


source = ab.get_source(
    "source-faker",
    config={"count": 10000, "seed": 0, "parallelism": 1, "always_updated": False},
    install_if_missing=True,
)

# load secrets from GSM using the GCP_GSM_CREDENTIALS env variable
secret_client = secretmanager.SecretManagerServiceClient.from_service_account_info(
    json.loads(os.environ["GCP_GSM_CREDENTIALS"])
)
secret = json.loads(
    secret_client.access_secret_version(
        name="projects/dataline-integration-testing/secrets/AIRBYTE_LIB_SNOWFLAKE_CREDS/versions/latest"
    ).payload.data.decode("UTF-8")
)

cache = SnowflakeSQLCache(
    SnowflakeCacheConfig(
        account=secret["account"],
        username=secret["username"],
        password=secret["password"],
        database=secret["database"],
        warehouse=secret["warehouse"],
        role=secret["role"],
    )
)

source.check()

source.set_streams(["products"])
result = source.read(cache)

for name in ["products"]:
    print(f"Stream {name}: {len(list(result[name]))} records")
