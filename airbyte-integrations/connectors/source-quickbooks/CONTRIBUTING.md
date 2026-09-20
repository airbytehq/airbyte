# Contributing to source-quickbooks

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Request pacing: `api_budget` and `concurrency_level`

All 28 streams query the same endpoint (`GET /v3/company/{realm_id}/query`) against the single
realm configured on the connection, so Intuit's per-realm ceilings map directly onto the
connection. The manifest therefore uses one global `MovingWindowCallRatePolicy`
(`matchers: []`) rather than per-stream policies.

Intuit's [published limits](https://help.developer.intuit.com/s/article/API-call-limits-and-throttling):

| Limit | Scope | Applies here |
| --- | --- | --- |
| 500 requests / minute | realm ID | Yes |
| 10 concurrent requests | realm ID + app | Yes |
| 40 batch requests / minute | realm ID | No — this connector issues no batch requests |

The configured rates are `8` per `PT1S` and `300` per `PT1M`, with `max_concurrency: 10` and a
user-tunable `num_workers` defaulting to `4`.

Why below the published ceilings:

- The budget only sees requests this connector makes. The same realm can also be consuming
  quota through the QuickBooks UI or other apps, so syncing at 500/min would leave no room for
  anything else and produce 429s the connector cannot predict.
- Intuit's own community threads
  ([example](https://help.developer.intuit.com/s/question/0D54R0000AEIpiVSQT/the-api-call-limits-throttles-says500-requests-per-minute-per-realm-id))
  disagree on whether 500/min is strictly per realm or partly shared per app across realms.
  Headroom keeps the connector correct under the stricter reading.

Why two rates instead of one 300/min rate: `MovingWindowCallRatePolicy` enforces a *moving*
window, so a single coarse rate permits the whole minute's quota to be spent in a burst and
then blocks for the rest of the window. Layering a per-second rate under the per-minute rate
keeps the request stream smooth, and the per-second rate also bounds how many requests can be
in flight at once, staying under Intuit's 10-concurrent-request ceiling regardless of how
`num_workers` is set.

`ratelimit_reset_header` is deliberately left unset. `HttpAPIBudget.get_reset_ts_from_response`
passes the header value straight to `datetime.fromtimestamp()`, which is only correct for epoch
**seconds**. QuickBooks' 429 response headers have not been observed from this repository, so
wiring a reset header without that evidence risks scheduling a reset far in the future. The
budget is proactive pacing; the CDK's default retry behavior remains the reactive safety net.

These values are conservative by choice, not measured: this repository has no working QuickBooks
credential, so no live sync was used to tune them.

## Pagination

Each stream's query template requests `MAXRESULTS {{ (config.max_results or '200') | int }}`
and the paginator's `OffsetIncrement.page_size` uses the same expression. The two must stay in
sync. `OffsetIncrement` advances the offset by the number of records actually returned, and uses
`page_size` only for the stop condition (`last_page_size < page_size`). If `page_size` is smaller
than the requested `MAXRESULTS`, a full page never satisfies the stop condition, so every drained
30-day slice costs one extra request that returns no records.

`max_results` is not exposed in the connector spec; it exists only as an escape hatch for configs
that set it directly.

## `maxSecondsBetweenMessages`

`metadata.yaml` sets `maxSecondsBetweenMessages: 86400`. This is not derived from measured stream
timings — none exist for this connector. It is intentionally loose: a heartbeat tighter than the
slowest realm's worst case turns a slow-but-healthy sync into a hard failure.
