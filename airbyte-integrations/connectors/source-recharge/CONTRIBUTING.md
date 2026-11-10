# Contributing to source-recharge

For general guidance on contributing to Airbyte connectors, see the
[Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Unique behaviors (summary)

Full technical detail for each item lives in [AGENTS.md](./AGENTS.md).

1. **The `events` Stream Is Hard-Capped to a Rolling 7-Day Window** — Recharge only serves the last
   seven days of events, so the connector floors that stream's start date at seven days ago; a
   historical `start_date`, a saved sync position from a long-paused connection, and any
   `lookback_window_days` setting are all silently overridden for `events` alone. Widening or removing
   that floor makes the API reject the request, which fails the whole sync rather than just this
   stream.
2. **Cursor Pages Omit Sorting and Date Filters** — Recharge accepts only the cursor and page size
   after the first cursor-paginated request. Keep sorting and date filters on the first page only,
   except for the deprecated orders API, which needs them on every page.
3. **Orders Switches API Versions and Keeps a Naive Cursor** — The orders API option selects either
   deprecated page-number pagination or modern cursor pagination; an omitted option selects modern.
   Orders preserves the API's naive US-Eastern time convention and resumes inclusively without a
   lookback window, so changing timestamps or slice pagination can skip records.
