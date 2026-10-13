# Contributing to source-ramp

For general guidance on contributing to Airbyte connectors, see the
[Connector Development documentation](https://docs.airbyte.com/connector-development/).

This is a manifest-only connector: all behavior lives in `manifest.yaml`. It reads Ramp's developer API.

## Unique behaviors (summary)

Full technical detail for each item lives in [AGENTS.md](./AGENTS.md).

1. **One token request asks for every scope, and Ramp silently drops the ones the app lacks** -- A missing
   read scope never breaks the login; it fails only the stream that needs it, with a message naming the
   scope. Keep the single shared scope list.
2. **Ramp's own error codes drive the error mapping, including a 404 for a bad token** -- Auth and scope
   failures are config errors with actionable messages, keyed on Ramp's error codes. Ramp reports a
   rejected token as a 404, so never treat a 404 as "not found" on the shared error handler.
3. **Several list endpoints hide records unless asked** -- Ramp drops declined transactions, repayments,
   suspended users, terminated funds and archived records, and leaves some fields empty, unless the request
   asks for them. Removing one of those parameters silently loses rows.
4. **Deletions are replicated as a flag field on the primary stream** -- Archived, terminated and
   deactivated records keep syncing with their final state; there are no separate deleted-record streams.
   Terminated cards and deleted reimbursements are the known gaps.
5. **`cards` reads a legacy endpoint that Ramp no longer documents** -- It still works but never returns
   terminated cards, and moving to the documented card endpoints would be a breaking change.
6. **Only three streams are incremental, and `transactions` relies on an undocumented filter** --
   `transactions` and `reimbursements` sync by update time and `receipts` by creation time; everything else
   is full refresh because Ramp offers no update-time filter.
7. **`business_balance` has no primary key** -- Ramp returns a single balance snapshot with no identifier,
   so this stream is the connector's one deliberate keyless exception.
8. **`vendor_contacts` skips vendors that return 404** -- A vendor deleted mid-sync is skipped instead of
   failing the stream.
9. **Date fields are typed, except three that Ramp does not return in ISO 8601** -- `cards.expiration` and
   the two `business_balance` billing dates stay strings because of their formats. Changing the type of an
   existing field is a breaking change, so type new date fields when you add them.

## Testing

- Unit tests in `unit_tests/` mock Ramp's API and run without credentials.
- Connector CI reads every stream against Ramp's sandbox (`demo-api.ramp.com`) with the
  `SECRET_SOURCE-RAMP-SANDBOX__CREDS` secret. A new stream's read scope must be granted to that sandbox app
  before CI can read it, and the sandbox needs at least one record for the stream (and for each partition).
