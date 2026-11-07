# Contributing to source-amazon-seller-partner

For general guidance, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Unique behaviors (summary)

Full technical details for each item live in [AGENTS.md](./AGENTS.md).

1. **Report Responses Are Gzip-Compressed CSV, XML, or JSON (Not Standard REST)** — Report formats differ by stream and sometimes by marketplace. Select the right decoder and preserve date-boundary rules.
2. **Reactive Token Invalidation on 403 Errors** — Expired tokens trigger a refresh before retrying. Keep this behavior separate from permission errors.
3. **Reciprocal Retry-After Header for Backoff** — Amazon returns requests per second rather than a wait duration. The connector inverts the value before waiting.
4. **Regression Tests Will Not Run for This Connector** — Local OAuth/regression testing has known limitations. Validate releases on an isolated Cloud connection.
5. **Standard Tests Will Not Pass for All Streams** — Some vendor forecasting reports reject the sandbox account type. These permission failures predate this change.
6. **Known Stream Failures in Testing** — Sandbox permissions and report availability cause known failures. Check the detailed list before treating them as regressions.
7. **Report Streams Must Declare Their Own `dataStartTime`/`dataEndTime`** — Each report must retain its date bounds when overriding its request body. Daily reports also need calendar-day boundaries.
8. **Vendor retail analytics reports forward report options but supply no defaults** — Required options depend on the account. Missing or invalid options must remain visible to the user.
9. **Vendor retail analytics streams must hold back four days** — Amazon publishes these reports with a delay. Requesting newer periods can fail the sync.
10. **FATAL reports must surface Amazon's reason** — Failed reports can carry an explanatory document. Preserve the distinction between configuration errors and retryable failures.
11. **Settlement Reports Use `AsyncRetriever` Without Creating Anything** — Amazon generates settlement reports automatically. Fetch download URLs only when ready to use them because they expire quickly.
12. **Brand Analytics Requests Must Cover Complete Weeks** — Supported reports backfill complete Sunday–Saturday weeks within the two-year lookback and resume from the saved week. Generic time-window and lookback settings must not split a reporting week.
13. **Inbound Items Checkpoint Through Their Parent Shipments** — Items inherit a shipment-window watermark rather than an Amazon update timestamp. Cap future end dates at now, preserve nested parent state, and use fixed mode to recover history beyond the configured rolling window.
