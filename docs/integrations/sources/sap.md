# SAP

This source reads data out of SAP systems through the [ERPL](https://erpl.io) DuckDB
extensions. One connector covers four SAP interfaces; you pick one per connection.

| Protocol | Reads |
|---|---|
| SAP Tables and CDS Views (RFC) | Any transparent table, pool/cluster table or CDS view, via `RFC_READ_TABLE` |
| SAP BW Queries (BICS) | BW InfoProviders and BEx queries, including variable binding |
| SAP ODP (RFC) | ODP providers in the BW, ABAP_CDS, SAPI, SLT and HANA contexts, full and delta |
| SAP ODP (OData) | The same ODP data over the SAP Gateway, full and delta |
| SAP RFC Function Modules | Any remote-enabled function module or BAPI, called with your parameters |

## Prerequisites

- A SAP NetWeaver or S/4HANA system reachable from wherever Airbyte runs.
- A service user in the client you want to replicate. A user type of
  *Communication* (`C`) is enough, and its password should be set not to expire —
  otherwise the sync fails on the day it lapses.
- Authorization object **`S_RFC`** for the function groups the connector calls.
  The minimum by protocol:

  | Protocol | Function groups / modules |
  |---|---|
  | Tables and CDS views | `RFC_READ_TABLE` (or a custom equivalent), `DDIF_FIELDINFO_GET` |
  | Function modules | `RPY_FUNCTIONMODULE_READ`, plus every module you configure |
  | BW queries | `BICS_CONS_CREATE_DATA_AREA`, `BICS_PROV_OPEN`, `BICS_PROV_GET_INITIAL_STATE`, `BICS_PROV_SET_STATE`, `BICS_PROV_GET_RESULT_SET`, `BICS_PROV_VAR_GET_VARIABLES`, `BICS_PROV_CLOSE` |
  | ODP over RFC | the `RODPS_REPL_*` group (`..._CONTEXT_GET_LIST`, `..._ODP_GET_LIST`, `..._ODP_OPEN`, `..._ODP_FETCH`, `..._ODP_CLOSE`) |
  | ODP over the Gateway | an activated ODP OData service, reachable over HTTPS |

  BW additionally checks its own analysis authorizations (`S_RS_COMP`,
  `S_RS_AUTH`) on the InfoProvider — a BW question, granted as it would be for a
  person running the query. The full list, with every module the connector can
  call, is in [authorizations](https://github.com/DataZooDE/erpl-airbyte/blob/main/docs/authorizations.md).

Fill in **either** a direct logon or a load-balanced one:

| Setting | Needed for | Notes |
|---|---|---|
| **Application Server Host** + **System Number** | direct logon | the usual choice |
| **Message Server Host** + **System ID** + **Logon Group** | load-balanced logon | use instead of the two above |
| **Client**, **User**, **Password** | always | password is optional under SNC or SSO2 |
| **Language** | optional | two letters; only affects field texts |
| **Gateway Base URL** | ODP over OData | scheme and port, e.g. `https://sap.example.com:44300` |
| **SAProuter String** + **SAProuter Host** | behind a SAProuter | the string is the `/H/…/S/…` route; the host is the bare hostname, which is what the platform needs to allow egress |
| **Enable SNC**, **SNC Partner Name**, **SNC Library Path**, **SNC Quality of Protection** | encrypted RFC | see Security below |

## Setup guide

### For Airbyte Cloud:

This connector is **not available on Airbyte Cloud**. It loads native DuckDB
extensions and speaks SAP's RFC protocol, which needs network access to a system
inside your own landscape. Run it on Airbyte Open Source or Self-Managed.

### For Airbyte Open Source:

1. Create a new source and choose **SAP**.
2. Fill in the logon fields from the table above.
3. Choose a **Protocol** and tell the connector what to read:
   - a **pattern** (`table_pattern`, `query_pattern`, `name_pattern`,
     `service_pattern`) to discover objects in bulk, and/or
   - an explicit **objects** list, which is also where per-object settings live
     (columns, SAP-side filters, cursor field, BEx variables, ODP subscriber name).
4. Run the connection test, then **Set up source** and refresh the schema.

BEx queries with mandatory variables must be listed explicitly with those
variables bound — BW refuses to return a result until they have values.

## Calling function modules

The **SAP RFC Function Modules** protocol turns a call to a remote-enabled function
module into a stream. Each entry under **Function Modules** names the module, the
result parameter whose rows become the records (**Result Parameter**, e.g.
`/FLIGHT_LIST`), and the **Parameters** to pass. Leave the result parameter empty to
emit the module's scalar export parameters as a single record.

Parameter values are written as JSON and cast to the SAP type the module declares, so
a date can be given either as `20260102` or `2026-01-02`. Nested SAP structures and
table parameters are written as JSON objects and arrays.

**Slice By** calls the module once per value of one parameter, in parallel, and unions
the results — useful for a BAPI that only accepts one company code or airline per call.

:::warning
The connector cannot tell a function module that reads from one that writes. Only the
modules you list are ever called, and discovery never calls them at all — schemas come
from the module's interface metadata. Choosing read-only modules is your
responsibility. Give the connector's SAP user `S_RFC` authorization for exactly the
function groups it needs and no more.
:::

Failures are not silent: a BAPI that answers with `TYPE = 'E'` or `'A'` in its `RETURN`
table fails the stream with the SAP message attached, rather than syncing zero records.

## Supported sync modes

| Feature | Supported |
|---|---|
| Full Refresh - Overwrite | Yes |
| Full Refresh - Append | Yes |
| Incremental - Append | Yes (RFC and function modules with a cursor field; BW with a watermark variable; both ODP protocols) |
| Incremental - Append + Deduped | Yes |
| Change Data Capture | Yes, for both ODP protocols |
| Namespaces | No |

**Function modules** sync incrementally when you set both a **Cursor Field** (a result
column) and a **Cursor Parameter** (the import parameter the stored value is passed to
on the next run).

**RFC** syncs incrementally when you nominate a **Cursor Field** — a date or
timestamp column. The connector keeps the highest value it has seen and pushes a
`>=` predicate down to SAP on the next run.

**BW queries** sync incrementally through a BEx variable used as a watermark:
set **Cursor Variable**, **Cursor Field** and a **Primary Key**. The selection is
`>=`, so the boundary period is re-read each run and the key is what lets the
destination deduplicate it.

**ODP** syncs incrementally through SAP's own delta mechanism. The first
incremental run performs SAP's DELTAINIT: it returns the whole current snapshot
and registers a subscription. Later runs return only what changed, and deletes
arrive as `_ab_cdc_deleted_at` tombstones.

:::caution
The ODP delta position lives **on the SAP system**, in an ODQ subscription keyed
by a *subscriber process*. Two consequences:

- **Set `subscriber_process` explicitly when more than one Airbyte connection
  reads the same ODP object from the same SAP system.** The Airbyte protocol
  gives a connector no connection identifier, so the derived name is built from
  the SAP logon (system, client, user) and the object. Two connections with the
  same logon derive the *same* name, share one subscription, and consume each
  other's changes — each seeing only part of the delta, permanently. The
  connector logs a warning whenever it derives a name.
- **Deleting a connection without resetting the stream strands the subscription**
  on SAP, where it keeps retaining delta data. Reset the stream first, or clear
  it in transaction `ODQMON`.
:::

## Supported Streams

Streams are whatever your pattern and object list select. Stream names are:

- **RFC** — the SAP table or view name, e.g. `SFLIGHT`
- **BICS** — the name you give the object
- **ODP (RFC)** — `<context>/<provider>`, e.g. `ABAP_CDS/SEPM_IBUPA$P`
- **ODP (OData)** — the entity-set name, e.g. `FactsOfZJRODPVSQL`
- **Function modules** — the name you give the entry

## Performance

- **Columns** is the setting that matters most. Naming the fields you actually
  want pushes the projection into SAP and was worth **3.8x** on a 55-column table.
- **Partitions** (RFC) splits one table scan into row ranges read in parallel,
  and is **off by default** because it only helps narrow extracts: measured on a
  164,673-row table, partitioning was slower at every setting tried, on both a
  wide and a narrow extract. The connector scales the SAP fetch budget with the
  partition count automatically, which removed one cause of that; a further
  penalty remains unexplained. Raise it only with a measurement in hand. Rows then arrive in an unspecified order, which does not affect
  correctness. See [performance](https://github.com/DataZooDE/erpl-airbyte/blob/main/docs/performance.md).
- **Threads** (ODP) parallelises full extractions. Delta extractions always run
  single-threaded: a parallel multi-package delta can under-count.
- **Concurrency** controls how many streams are read at once. Each worker holds a
  SAP connection, so keep it within the system's free work processes.
- **BICS cannot paginate** — BW materialises the entire result set or none of it.
  For a large cube, use **Slice By** to run one BICS session per characteristic
  member and bound memory.

## Data type map

SAP's DDIC types are mapped to JSON Schema as follows. Anything not listed
arrives as a string, which is lossless.

| SAP (DDIC) | Airbyte type | Notes |
|---|---|---|
| `CHAR`, `STRING`, `LANG`, `CUKY`, `UNIT`, `CLNT` | `string` | |
| `NUMC`, `ACCP` | `string` | leading zeros are significant, so these stay text |
| `INT1`, `INT2`, `INT4`, `INT8` | `integer` | |
| `DEC`, `CURR`, `QUAN`, `DECF16`, `DECF34` | `number` (big) | exact decimals; a `DEC` with no decimal places becomes an integer |
| `FLTP` | `number` | |
| `DATS` | `date` | `YYYYMMDD` on the wire |
| `TIMS` | `time` | `HHMMSS` on the wire |
| `UTCLONG`, `UTCL`, `UTCS`, `UTCM` | `date-time` | |
| `RAW`, `LRAW`, `RAWSTRING` | `string` (base64) | |

ODP streams additionally carry `_ab_cdc_deleted_at`, set when SAP reports a row
as deleted — provided the provider reports deletes at all. Over the Gateway an
entity set without a change-mode column cannot, and discovery warns when it finds
one.

## Security notes

- The ERPL extensions are downloaded over HTTPS at **image build time** and
  verified against checksums pinned in `bin/checksums.txt`; a mismatch fails the
  build. A sync makes no request to `get.erpl.io`.
- They are unsigned native code, so DuckDB runs with `allow_unsigned_extensions`.
  The extension directory is baked into the image and owned by the image user;
  do not point `ERPL_EXTENSION_DIR` at a directory other users can write.
- Entity-set URLs for **SAP ODP (OData)** are confined to the configured
  **Gateway Base URL** — an absolute URL naming another host is rejected rather
  than fetched with the Gateway's credentials.
- `snc_mode` defaults to `"0"` (unencrypted RFC), and a plain `http` base URL
  sends credentials in the clear. Both are fine against a local trial system and
  wrong against anything else: enable SNC and use `https` in production.

## Limitations & Troubleshooting

- The connector image is **linux/amd64 only**; ERPL publishes no arm64 build.
- BICS exposes no change tracking, so BW queries are full-refresh only.
- ODP OData catalog discovery depends on the Gateway catalog service, which is not
  reachable on every release. List entity-set URLs explicitly if discovery finds nothing.

### Common failures

| Symptom | Cause and fix |
|---|---|
| `RFC_ERROR_LOGON_FAILURE` | Wrong client, user or password, or the password expired. Service users should be type *Communication* with a non-expiring password. |
| `No authorization to access Function Group` | `S_RFC` is missing the group in the Prerequisites table. The message names the group. |
| `ILLEGAL_REQ_STATE_FOR_CONFIRM` on an ODP delta | A previous run failed mid-fetch and SAP would not close its cursor. The next run recovers it; `PRAGMA sap_odp_drop` clears it sooner. |
| A BW query returns no rows and logs a variable warning | A mandatory BEx variable is unbound. `RSRT` shows which; bind it in the object's `variables`. |
| `Failed to initialise the ERPL extensions` | The image is missing its native artefacts — not a SAP problem. |
| A sync is killed with no error | Out of memory. One wide stream needs ~1.7 GB, and concurrency multiplies it. |

More, including stranded ODP subscriptions and how to reset a stream, in
[troubleshooting](https://github.com/DataZooDE/erpl-airbyte/blob/main/docs/troubleshooting.md) and [operations](https://github.com/DataZooDE/erpl-airbyte/blob/main/docs/operations.md).

## Changelog

| Version | Date | Pull Request | Subject |
|---|---|---|---|
| 0.1.0 | 2026-09-12 | — | Rewrite as a single `source-sap` connector: adds BICS, ODP over RFC and ODP over OData alongside the existing table reads; moves to the Concurrent CDK with incremental sync, parameterised credentials and extensions baked into the image. |
