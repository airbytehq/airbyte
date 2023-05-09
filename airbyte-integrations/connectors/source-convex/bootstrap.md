# Convex

## Overview

Convex is the reactive backend-as-a-service for web developers.
As part of the backend, Convex stores developer-defined documents in tables.
Convex's HTTP API allows a developer to retrieve documents from their Convex tables.

## Endpoints

Convex defines three endpoints used for extracting data:

1. `/json_schema` identifies the data format for each table.
2. `/list_snapshot` returns pages of a table's data at a snapshot timestamp, for initial sync.
3. `/document_deltas` returns pages of modifications to a table's data after a given timestamp.

For more details, see the documentation for Convex Sync endpoints at
[https://docs.convex.dev/http-api/#sync](https://docs.convex.dev/http-api/#sync).
