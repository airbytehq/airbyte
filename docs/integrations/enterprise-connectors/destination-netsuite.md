---
dockerRepository: airbyte/destination-netsuite
enterprise-connector: true
---
# NetSuite

<HideInUI>

This page guides you through setting up the NetSuite destination connector, which writes warehouse data into NetSuite records (data activation, also called reverse ETL).

</HideInUI>

The NetSuite destination writes records to NetSuite with the SuiteTalk REST Record API. It can insert records, upsert them on `externalId`, and update them by internal ID. It works with standard records such as customers, contacts and sales orders, with custom records, and with custom body, entity and line fields.

## Prerequisites

- A NetSuite account (production or sandbox) with **REST Web Services** and **OAuth 2.0** enabled under Setup > Company > Enable Features > SuiteCloud.
- An integration record that allows the **Client Credentials (Machine to Machine)** grant and the **REST Web Services** scope.
- A role for Airbyte with the permissions listed below, assigned to the user that the certificate is mapped to.
- An RSA (at least 3072 bits) or EC (P-256) key pair and a self-signed certificate.

Token-based authentication (TBA) is not supported. NetSuite stops accepting new TBA integrations in release 2027.1.

### Role permissions

| Permission | Level |
| --- | --- |
| Setup > REST Web Services | Full |
| Setup > Log in using OAuth 2.0 Access Tokens | Full |
| Lists > Customers, Contacts (and any other record type you write) | Edit or Full |
| Transactions > Sales Order (and any other transaction you write) | Edit or Full |
| Lists > Items, Subsidiaries, Locations and other records your references point to | View |
| Custom record types you write | Edit or Full |

NetSuite issues access tokens even when REST access is not allowed. If the integration record lacks the **REST Web Services** scope, or the mapped role lacks a permission, REST calls answer `401 INVALID_LOGIN` although the token was issued. The reason is in Setup > Users/Roles > User Management > View Login Audit Trail.

Standard roles such as Data Warehouse Integrator cannot be edited. Map the certificate to a custom role, or to Administrator in a sandbox.

## Setup guide

### Step 1: Create the certificate

```bash
# RSA, signs with PS256
openssl req -new -x509 -newkey rsa:4096 -keyout private.pem -sigopt rsa_padding_mode:pss \
  -sha256 -sigopt rsa_pss_saltlen:64 -out public.pem -nodes -days 730

# or EC, signs with ES256
openssl req -new -x509 -newkey ec -pkeyopt ec_paramgen_curve:prime256v1 -nodes -days 730 \
  -keyout private.pem -out public.pem
```

`private.pem` is a PKCS#8 key (`BEGIN PRIVATE KEY`), which is what the connector expects. To convert an older key, run `openssl pkcs8 -topk8 -nocrypt -in key.pem -out private.pem`.

### Step 2: Set up NetSuite

1. Go to Setup > Integration > Manage Integrations > New. Name it Airbyte, select **Client Credentials (Machine to Machine) Grant** and the **REST Web Services** scope, and save. Copy the **Client ID**.
2. Go to Setup > Integration > Manage Authentication > OAuth 2.0 Client Credentials (M2M) Setup > Create New. Select the integration user, the Airbyte role and the integration, upload `public.pem`, and save. Copy the **Certificate ID**.
3. Note the **Account ID** from Setup > Company > Company Information. Sandbox IDs end in a suffix such as `_SB1`.

Certificates expire, and refreshing a sandbox removes its certificate mappings. Recreate the mapping after a sandbox refresh.

### Step 3: Set up the destination in Airbyte

1. In Airbyte, go to Destinations > New destination and select **NetSuite**.
2. Enter the **Account ID**, **Client ID** and **Certificate ID**, paste the contents of `private.pem` into **Private Key**, and pick the **Signature Algorithm** that matches the key.
3. Optionally, open the **Advanced** section. In **Record Types**, list the NetSuite record types to offer as destination objects, using their REST names, for example `customer`, `contact`, `salesOrder` or `customrecord_project`. Names are case sensitive.
4. Optionally configure rejected records storage.
5. Select **Set up destination**. The check requests a token, reads the metadata of each record type, and writes a test file to the rejected records storage.

### Step 4: Map fields

Create a data activation connection from your warehouse. For each stream, choose a record type and an operation, then map source columns to NetSuite field IDs. The destination offers the fields the role can write, including custom fields. You can also type a field ID that is not listed.

## Supported operations

| Operation | Request | Matching key | Notes |
| --- | --- | --- | --- |
| Insert | `POST /record/v1/{type}` | none | Not idempotent. A replayed record creates a second record. |
| Upsert | `PUT /record/v1/{type}/eid:{externalId}` | `externalId` | Creates or updates. Safe to replay. Recommended. |
| Update | `PATCH /record/v1/{type}/{id}` | `id` (internal ID) | Updates existing records only. Can set `externalId`, which is how existing records get their source ID before switching to upsert. |

Only mapped fields are sent, so NetSuite fields outside the mapping are never changed. Null values are skipped unless **Null Values** is set to `send_null`.

## Field values

The source row should already use NetSuite field IDs and internal IDs. The destination only changes value shapes:

| Field type | Source value | Sent to NetSuite |
| --- | --- | --- |
| Reference or list (entity, subsidiary, item, custom list) | internal ID, such as `123` | `{"id": "123"}` |
| Reference by external ID, for a parent created in the same sync | JSON text `{"externalId": "001ABC"}` | sent as is |
| Subrecord (shippingAddress) | JSON object or JSON text | sent as is |
| Sublist (item, addressBook) | JSON array of lines, as an array or JSON text | `{"items": [...]}` |
| Multi-select | JSON array of internal IDs | `{"items": [{"id": ...}]}` |
| Date | `2026-11-06` or a timestamp | `2026-11-06` |
| Number, integer, boolean | number, boolean, or text | coerced to the declared type |

Inside sublist lines, reference fields such as `item`, `location` and `department` also take plain internal IDs.

### Sales order lines

Send the lines of each order as one JSON array column. In Snowflake, for example:

```sql
select
    o.sf_order_id                                   as "externalId",
    o.ns_customer_id                                as "entity",
    o.order_date                                    as "tranDate",
    array_agg(object_construct(
        'item', l.ns_item_id,
        'quantity', l.quantity,
        'rate', l.unit_price,
        'custcol_sf_line_id', l.sf_line_id
    )) within group (order by l.line_number)        as "item"
from orders o
join order_lines l on l.order_id = o.order_id
group by 1, 2, 3
```

With **Replace Sublists** on (the default), upserts and updates send `?replace=item`, so NetSuite replaces the lines instead of adding to them. Re-sending an order does not duplicate its lines.

### Parents and children in the same sync

NetSuite rejects a child record, such as a sales order, if its parent, such as the customer, doesn't exist yet. Airbyte writes streams in parallel and doesn't order them, so a child can arrive before its parent in the same sync. That child is rejected with an invalid reference error, and the sync cursor still moves past it.

To avoid this:

- Upsert parents and children on `externalId`, and reference parents with `{"externalId": "..."}`.
- Sync parents in their own connection, scheduled before the connection that writes children. Or exclude, in the child model, children whose parent hasn't been written yet, for example by joining to a table of synced parents.
- Rows the child model held back get picked up by a later sync, because upserts are safe to replay.

## Rejected records

When NetSuite refuses a record, for example for a missing required field or an invalid reference, the sync continues and the record goes to rejected records storage. Each rejected record keeps its source fields and gains:

| Field | Content |
| --- | --- |
| `_netsuite_http_status` | HTTP status from NetSuite |
| `_netsuite_error_code` | NetSuite error code, such as `USER_ERROR` or `INVALID_KEY_OR_REF` |
| `_netsuite_error_message` | NetSuite error detail |
| `_netsuite_error_path` | Field the error refers to, when NetSuite reports one |
| `_netsuite_error_body` | Full error response |
| `_netsuite_request` | Operation and record, such as `PUT salesOrder/eid:006X` |

Records that cannot be turned into a request, such as a missing matching key or malformed JSON lines, are rejected with `_netsuite_error_code` set to `INVALID_RECORD`.

Rejected records storage supports Amazon S3 today. To query rejected records in Snowflake, create an external stage on the bucket and load the files with Snowpipe or `COPY INTO`.

The sync fails instead of rejecting records when the failure is not about the record: invalid credentials or missing role permissions, concurrency limits that do not clear, or 20 records in a row failing with NetSuite server or network errors.

## Performance and limits

- Each record is one request. **Max Concurrent Requests** (default 3) caps parallel requests. NetSuite shares one concurrency pool across REST, RESTlets and SOAP for the account, so leave room for other integrations.
- Concurrency and rate limit errors (HTTP 429) pause all requests, honor `Retry-After`, and retry with exponential backoff and jitter.
- Server errors and network errors are retried for upserts and updates. Inserts are not resent after a timeout, because NetSuite may already have created the record; they are rejected with code `AMBIGUOUS_TIMEOUT`.
- Saving a record runs NetSuite user event scripts and workflows, as in the UI. Slow scripts slow the sync; raise **Request Timeout** if saves take longer than three minutes. A failing script rejects the record with the script's error message. Check script deployments on the record type if every record of one type is rejected with the same error.
- SuiteApps and customizations can deploy user event scripts on sales orders and other records that also run for REST requests. If such a script fails for REST requests, every record of that type is rejected with the script's error. Before go-live, review the script deployments on each record type you write (Customization > Scripting > Script Deployments), and limit their execution context where needed.
- Each integration record has its own concurrency limit (Setup > Integration > Manage Integrations, Max Concurrency Limit). Keep **Max Concurrent Requests** at or below it.
- Airbyte checkpoints after each batch (**Batch Size**, default 50) once every record in it is written or rejected.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
| :------ | :--- | :----------- | :------ |
| 0.1.0 | 2026-11-08 | [481](https://github.com/airbytehq/airbyte-enterprise/pull/481) | New destination: insert, upsert and update with OAuth 2.0 M2M |

</details>
