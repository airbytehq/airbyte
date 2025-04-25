# Track PMS Migration Guide

## Upgrading to 4.0.0
Updates the units schema and removes `units.isOccupied` and `units.cleanStatusType`. These don't return results in our testing.

Please account for any downstream changes to `units` (e.g. remove database columns).

Readded `reservations.guestBreakdown` to make the reservation rates available; however this doesn't typically return results so no declared schema has been alotted for it.
Reservation rates  are also present in `reservations.quoteBreakdown` if `guestBreakdown` doesn't have any values.

Other updates include fixes to the stream API links in the connector docs and updating error filter criteria - reducing 429 error retries from 10 to 3, and specifing a 409 error method.
* The constant backoff strategy appears to be working (these seemed to be exponential in Airbyte versions < v1.5.1).
* The Track API errouneous 409 error is set to one retry, though 0 would be preferred (the Airbyte UI, as of v1.5.1, automatically removes the number of retries alltogether if 0). Might have to circle back on this one.

## Upgrading to 3.0.0

The redundant `_embedded` field has been removed from the following streams:
* `accounting_accounts`
* `accounting_bills`
* `accounting_charges`
* `accounting_deposits`
* `accounting_transactions`
This redundant information was also prone to contain unnecessary sensitive information, like SSNs.

Accounting_accounts added a query parameter `includeRestricted=1` to pull more comprehensive account information.

The duplicated `owners_statements_transactions_pii_redacted` was dropped - it had the same configuration as `owners_statements_transactions`.

The duplicated `folios_master_rules` was dropped - it had the same configuration as `folio_rules`.

The `owners_statements_transactions._embedded` column was tweaked to keep only `paymentType` and `reservation`; other known fields obtainable by joining to other streams.

Please update and resynchronize all data from the above streams from your connections.

## Upgrading to 2.0.0

Streams have been renamed to follow the established convention and have been normalized. Please update and resynchronize all data from your connections.

This change renamed the following streams:
- `folio_logs` -> `folios_logs`

## Upgrading to 1.0.0

Streams have been renamed to follow the established convention and have been normalized. Please update and resynchronize all data from your connections.

