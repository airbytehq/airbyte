# Contributing to source-reddit-ads

For general guidance on contributing to Airbyte connectors, see the
[Connector Development documentation](https://docs.airbyte.com/connector-development/).

This is a manifest-only connector: all behavior lives in `manifest.yaml`. It reads Reddit's Ads API v3
for one ad account.

## Unique behaviors (summary)

Full technical detail for each item lives in [AGENTS.md](./AGENTS.md).

1. **Token refresh needs HTTP Basic client credentials and a Reddit User-Agent, and only the refresh sends `user_agent`** --
   The connector trades the refresh token for short-lived access tokens at `https://www.reddit.com/api/v1/access_token`
   and saves the new refresh token when Reddit rotates it. The configured User Agent (default
   `airbyte:source-reddit-ads:v1`) is sent only on that token request, never on the requests that read ads data.
2. **Report parent IDs come from breakdowns, and Reddit allows at most three** -- Reddit only returns a parent ID
   in a report row when it is a breakdown, so the ad group and ad reports add the campaign as one. With the
   three-breakdown limit used up, the ad report's ad group ID can be empty.
3. **Report windows are built in the request body so each window's last day isn't dropped** -- Reports are
   requested in contiguous three-day windows whose start and end times the connector sets itself. Report history
   stops at 24 months, the most Reddit serves.
4. **Report `date` is cut to `YYYY-MM-DD`, and rows without a string `date` are dropped** -- The report date
   always lands as a plain date, even if Reddit adds a time, and older saved state with a time still works.
   Rows with no date are skipped.
5. **Spend, cost and conversion-value metrics stay in Reddit's units** -- Spend and cost metrics stay in
   micro-units, and conversion values stay multiplied by 100. The connector doesn't convert them.
6. **Pagination decodes `%3D` in Reddit's page token** -- Reddit URL-encodes its next-page token, and the
   connector decodes it before sending it back. Without that, every stream stops after its first page.
7. **Two rate-limit groups with different quotas** -- Account, ad, ad group and campaign requests share a limit
   of 400 per minute, while report requests have their own limit of 60 per minute. The limits apply per sync,
   not across other apps using the same credentials.
8. **400 responses are split by message into ad-account and request errors** -- A bad ad account ID, a missing
   permission or an unknown account is reported as a configuration problem. Other invalid requests are reported
   as system errors, after rate-limit and server errors have been retried.

## Not implemented

- `business_account`: `GET /businesses/{business_id}` returns the business that owns the ad account (`ad_account.business_id`). It holds business contact details rather than advertising data and has its own rate-limit group, `ads-business-manager` (100 requests per 60 seconds).
- Custom conversion events by name: `/reports` returns them only for event names passed in `conversion_custom_events` (up to 20, case-sensitive), which the connector does not collect. Standard conversion metrics are already fields on every report stream.
- Other breakdowns such as country, region, community or keyword: each report stream breaks down only by IDs and `DATE`, because extra breakdowns multiply rows and change the primary key. From December 8, 2026 Reddit also rejects some breakdown combinations (https://ads-api.reddit.com/docs/v3/guides/programs/reporting/upcoming-reporting-api-changes).

## Deletions

The connector does not detect or emit deletions. In Reddit's OpenAPI spec, the
`configured_status` and `effective_status` enums of ads, ad groups and campaigns
include `DELETED`, and the ads list endpoint accepts `effective_status` (and
`configured_status`) filters that include `DELETED`; the ad group and campaign
list endpoints have no status filter. The connector sends no status filter, so it
doesn't request `DELETED` items explicitly, and it is unverified whether the
default list responses include them. Items Reddit lists are synced with their
status fields. If Reddit stops listing an item, its last-synced row stays in the
destination until a full refresh with overwrite replaces the table.

## Verification note

Read-only live checks against a test ad account with no delivery confirmed the
report request bodies (Reddit validates breakdown and field names), the
rate-limit groups and the `ad_account` and `ad_group` record shapes. The test
account's reports return no rows. Known from real data: parent IDs requested
only as `fields` don't appear in `campaign_report` rows (see AGENTS.md section 2), and a
comparison regression test on a customer connection with delivery showed the
26 integer-typed metrics as JSON integers and `date` as plain `YYYY-MM-DD`.
Report row keys otherwise rest on Reddit's OpenAPI spec and the hermetic tests.
