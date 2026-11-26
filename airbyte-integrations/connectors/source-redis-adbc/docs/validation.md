# Validation record

## Original standalone implementation

Validated on November 1, 2026, on Docker Desktop, Linux ARM64 containers.

### Components

| Component | Pinned version |
| --- | --- |
| Source Python runtime | 3.12.12, Debian Bookworm (base image digest in Dockerfile) |
| Airbyte Python CDK | 7.45.0 |
| Airbyte protocol Python models | 0.17.1 |
| ADBC driver manager / Flight SQL | 1.13.0 |
| PyArrow | 26.0.0 |
| Redis native driver | `redis/redis-adbc-driver@b99ec0aa3b61ed5db130211951d24191217efae8` |
| Redis Software | `redislabs/redis:8.2.0-78.18`, Redis 8.6.2, Search, one RAM shard, noeviction, QPF 4x |
| Airbyte PostgreSQL destination | 3.0.23, digest `sha256:1a122ed76f97b45fcdf7a8183bed93330a8f8eedad365e883d738774a35d69ea` |
| PostgreSQL | 16.10 |
| Flight SQL reference gateway | Apache Arrow Go 18.8.0 SQLite example server |

### Coverage

Final test results: 50 unit/CLI tests and 3 native Redis tests passed in the
packaged Python 3.12 image. The separate Flight SQL reference-server run passed
its integration test (54 tests total). Both PostgreSQL destination syncs passed.

- Unit and CLI tests: explicit conversions, large integers, decimal precision,
  dictionary values, binary, nanosecond timestamps, NULLs, nested values,
  unsupported types, non-finite numbers, exact schema filters, ambiguous
  catalogs, quoted identifiers, projection, drift failures, full-refresh-only
  enforcement, lazy batch requests, connection failure, late read failure and
  reader/cursor/connection cleanup on cancellation.
- Native Redis tests: check, discovery, projection, five records across at least
  three Arrow batches, empty results, repeat reads and abandoned readers.
- PostgreSQL destination test (`python3 scripts/e2e.py`): the source's actual
  spec/check/discover/read CLI and the official destination's check/write CLI.
  Five rows and an empty stream reach final PostgreSQL tables. Values include
  `9007199254740993`, `12345678901234567890.123456789`, explicit NULLs, booleans,
  Base64 binary and microsecond timestamps. The test compares final selected
  column values, checks that the empty table has zero rows, and repeats with a
  new Overwrite generation to verify exactly five rows remain.
- Failure/retry: an invalid selected stream fails before emitting records;
  a fresh full-refresh read succeeds. A failed native connection does not expose
  its password in CLI stdout/stderr. Late read errors and cancellation are
  separately injected in deterministic backend tests.
- Flight SQL (`bash scripts/test-flight-sql.sh`): an actual ADBC Flight SQL
  connection to Apache's SQLite reference server exercises check, metadata,
  schema discovery and selected-field reads, including a NULL row, through the
  same backend and source classes used for Redis.

The destination test supplies `generation_id`, `minimum_generation_id` and
`sync_id`, which the Airbyte platform normally adds. It invokes the connector
processes directly over JSON/stdio; it does not test a full Airbyte platform
deployment or the custom-source registration UI.

The first destination run exposed that CDK 7.45.0's standard serializer removes
NULL entries inside arbitrary record dictionaries. The connector uses the
CDK parser/command handlers and its own record-preserving serialization shim.
A regression test verifies nested and top-level NULLs on the serialized wire.

## Upstream Poetry package

The Airbyte contribution ports the same extraction/conversion code into the
standard connector layout, with `unit_tests`, `integration_tests`, metadata,
Poetry, MIT licensing, user documentation and an icon. The upstream package uses
`adbc-driver-redis==0.0.19`, whose platform wheels bundle the native library,
instead of compiling a driver inside a custom connector Dockerfile.

The standard Airbyte Python image template builds the connector with
`airbyte/python-connector-base:4.1.1` pinned by digest. The inspected runtime is
Python 3.13.14. The Poetry lock pins wheel hashes and all resolved dependencies;
CDK 7.45.0, ADBC manager/Flight SQL 1.13.0 and PyArrow 26.0.0 remain pinned.
`REDIS_ADBC_LIBRARY` provides an explicit override for a locally built library.

Validation on Linux ARM64:

- 50 unit/CLI tests passed with the Poetry-installed package on Python 3.13.14.
- All 3 native Redis tests passed against the disposable Redis Software endpoint
  using the packaged wheel (54 connector tests total including Flight SQL).
- Ruff 0.8.3 lint/format and mypy checks passed.
- The standard Airbyte image built and its `spec` command succeeded.
- The actual Flight SQL reference-server integration passed with the packaged image.
- Both PostgreSQL destination syncs passed with this native-wheel image, verifying
  every loaded field, the empty stream and Overwrite replay.
- The CDK in-process standard suite reported 3 passed, 19 skipped and 18 deselected.
  Live discovery/read scenarios are explicitly bypassed until an owned endpoint
  is available in upstream CI. These skips are not claimed as acceptance passes.

Commands are in the connector README. `scripts/e2e.py --test-image
 airbyte-redis-adbc-test:dev` additionally runs the native three-test fixture on
its disposable Redis Software server after building `Dockerfile.test`.

Cloud and OSS registry entries are disabled during this draft review. Review is
still needed for the custom Python/database contribution, native wheel support,
packaging policy and a stable live acceptance endpoint. The generic ADBC layer
is exercised through Redis and the SQLite Flight SQL reference server; a Redis
Flight SQL production gateway is not bundled or claimed validated.

## Remaining boundaries

Redis-backed production Flight SQL gateways, Flight TLS/authentication, deployed
Redis Cloud TLS/ACL combinations, destination outage mid-write and platform job
cancellation/retry orchestration require deployment-specific validation. The
connector is full-refresh only, with no snapshot isolation, CDC, persistent
checkpoint, native Arrow transport or performance claim. Concurrent writes and
TTL expiry are documented consistency limitations. The container was executed
on ARM64; an AMD64 release build has not been validated here.

Upstream maintainer guidance on an in-tree Airbyte integration and any new
batch transport remains separate work in the existing upstream discussion.
