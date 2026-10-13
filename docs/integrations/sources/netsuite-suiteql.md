# NetSuite SuiteQL

The NetSuite SuiteQL source replicates configured NetSuite tables through REST
Web Services. It generates `SELECT *` SuiteQL queries so source configurations
cannot transform data. This connector is distinct from the NetSuite source,
which reads Record API objects rather than SuiteQL query results.

## Prerequisites

- A NetSuite account with REST Web Services enabled
- A token-based authentication integration and access token
- A NetSuite role permitted to query each configured table

## Setup Guide

### Step 1: Enable NetSuite Access

Enable REST Web Services and token-based authentication in NetSuite. Create an
integration, assign a role with access to the records queried, and create an
access token for that integration and role. Store the resulting consumer and
token credentials in a secret manager.

See NetSuite's [authentication documentation](https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/section_4389727047.html) and [SuiteQL REST API documentation](https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/section_157909186990.html).

### Step 2: Set Up the Source in Airbyte

1. In Airbyte, select **Sources**, then select **New source**.
2. Choose **NetSuite SuiteQL**.
3. Enter a source name.
4. Enter the NetSuite realm, consumer key and secret, and token ID and secret.
5. Add one or more table names.
6. Optionally set a page size from 1 through 1000.
7. Select **Set up source**.

After discovery, configure primary-key and cursor fields in the Airbyte
connection catalog.

Table and field names must begin with a letter or underscore and contain only
letters, numbers, and underscores.

## Supported Sync Modes

All table streams support Full Refresh and Incremental Append + Deduped. The
connector formats the configured date or timestamp cursor with `TO_CHAR` into a
stable `cursor_ts` state field and uses a matching `TO_DATE` predicate on later
incremental reads. Inclusive cursor predicates can emit the state-boundary row
again; destination deduplication removes that duplicate.

## Supported Streams

Streams are defined by the `tables` array in source configuration. Each table
creates a stream using its `table_name`; its schema is inferred during
discovery from sampled rows. Empty results produce an open object schema until
a later discovery sees a row. NetSuite also omits null-valued fields from query
responses. The connector therefore loads optional schema hints from a packaged
`source_netsuite_suiteql/schemas/<table_name>.json` file. Properties from that
file are appended only when absent from sampled rows; discovery retains all
other sampled fields and their inferred types. The packaged `transactionLine`
schema contains known nullable custom fields.

## Pagination and Limits

The connector sends query requests to NetSuite's SuiteQL REST endpoint and
follows the `hasMore`, `offset`, and `count` response fields. NetSuite returns
at most 100,000 rows per SuiteQL query. Use SuiteAnalytics Connect when a table
sync must return more rows.

## IP Allow List

If your organization restricts access by IP address, add the [Airbyte Cloud IP
addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to
the allow list.
