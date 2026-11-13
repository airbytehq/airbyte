# Redis (ADBC) source

Proposed community full-refresh source for Redis through Apache Arrow ADBC.
See [user documentation](../../../docs/integrations/sources/redis-adbc.md),
[the upstream discussion](https://github.com/airbytehq/airbyte/discussions/36121),
[Redis tracker #172](https://github.com/redis/redis-adbc-driver/issues/172), and
[the original implementation](https://github.com/alberttwong/redis-airbyte-connector/pull/1).

The source consumes ADBC RecordBatchReader batches and emits Airbyte JSON/stdio
records. It does not introduce a native Arrow transport. Incremental state, CDC,
shared snapshots and performance improvements are not claimed.

## Development

Use Python 3.12–3.14. The standard Airbyte base image is pinned by digest and
currently contains Python 3.13.14. Poetry locks CDK 7.45.0, ADBC manager/Flight SQL
1.13.0, PyArrow 26.0.0 and `adbc-driver-redis==0.0.19`. That driver's Linux wheels
bundle the native library. `REDIS_ADBC_LIBRARY` optionally overrides its path
for testing a locally built driver. No Go compiler is needed in the source image.

```sh
poetry install
poetry run pytest -q unit_tests
poetry run source-redis-adbc spec
```

This connector follows the shared Poetry connector tasks. From this directory:

```sh
poe test-unit-tests
poe test-integration-tests
poe test-standard-tests
poe format-check
poe lint-check
```

Native tests skip unless `REDIS_URI` points to a disposable Search-enabled
Redis Software database. Flight SQL tests skip unless `FLIGHT_SQL_URI` points
to the reference server. The native fixture creates and drops uniquely named
tables. The acceptance configuration includes spec and failed connection tests;
live read acceptance coverage requires an owned test endpoint before registry
enablement. Cloud and OSS registries are disabled during this draft review.

## Image and destination tests

From this directory in the Airbyte checkout:

```sh
bash scripts/build-image.sh
docker run --rm airbyte/source-redis-adbc:0.1.0 spec
python3 scripts/e2e.py
bash scripts/test-flight-sql.sh
# Optional native fixture run using the test image:
# python3 scripts/e2e.py --test-image airbyte-redis-adbc-test:dev
```

The build script uses Airbyte's standard `docker-images/Dockerfile.python-connector`
with the base image from `metadata.yaml`. The disposable destination test starts
Redis Software with Search and QPF 4x plus PostgreSQL 16.10, runs the actual
source and official PostgreSQL destination CLIs, verifies all loaded fields and
an empty stream, and repeats Overwrite with a new generation. It removes its
containers and private network. Fixed credentials are confined to local test
containers. This tests connector processes directly, not Airbyte orchestration.

For a manual read, copy `examples/config.json` to ignored `secrets/config.json`
and set a reachable Redis URI. On Docker Desktop use `host.docker.internal`
for a database on the host. Discover first and create a configured catalog
using exact discovered properties; `examples/catalog.json` illustrates its shape.

```sh
docker run --rm -v "$PWD/secrets:/config:ro" airbyte/source-redis-adbc:0.1.0 check --config /config/config.json
docker run --rm -v "$PWD/secrets:/config:ro" airbyte/source-redis-adbc:0.1.0 discover --config /config/config.json
docker run --rm -v "$PWD/secrets:/config:ro" airbyte/source-redis-adbc:0.1.0 read --config /config/config.json --catalog /config/catalog.json
```

See `docs/validation.md` for results and boundaries. Apache Arrow and the Redis
native driver retain their own upstream licenses; the connector code is MIT.
