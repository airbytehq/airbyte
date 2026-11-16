# source-pardot: Unique Connector Behaviors

`CONTRIBUTING.md` summarizes the same behaviors for people, under the same numbers and titles. Keep the two files in step.

Vendor facts below come from the Account Engagement (Pardot) API documentation at [developer.salesforce.com/docs/marketing/pardot](https://developer.salesforce.com/docs/marketing/pardot/overview). No test account exists yet ([airbyte-internal-issues#18838](https://github.com/airbytehq/airbyte-internal-issues/issues/18838)), so nothing below was read from a live account. The mock server tests in `unit_tests/mock_server/` are the proof.

## 1. Errors Are Matched on the Vendor's Code in the Body

The vendor documents no HTTP status per error code and no `Retry-After` header ([Error codes](https://developer.salesforce.com/docs/marketing/pardot/guide/error-codes.html)). Every response filter in `definitions.error_handler` therefore reads the code in the body: `code` in version 5, `@attributes.err_code` in version 4, which only `email_clicks` uses. The CDK asks the filters before it checks the status, so a filter also matches a 200 that carries an error body.

| Response | Connector behavior |
| :-- | :-- |
| Code 122, or the text `Daily API rate limit met` | Fails at once, `transient_error`, with a message that the daily limit resets the next day. See section 2. |
| Code 66, more than five concurrent requests | Retried, whatever the HTTP status. |
| Code 184, invalid access token | Fails at once, `config_error`: check the `pardot_api` scope and that the user is synced to the business unit. |
| Code 201, business unit not found | Fails at once, `config_error`: check the ID and the host. The vendor returns it for the wrong host too. |
| Code 49, access denied | Fails at once, `config_error`, naming the stream's `required_ability`. |
| 429, 408 or 5xx without a known code | CDK default: retried. |
| 400, 401, 403 or 404 without a known code | CDK default: fails at once. |

Retries wait with `ExponentialBackoffStrategy` at factor 10, five retries at most: 21, 41, 81, 161 and 321 seconds. The CDK stops retrying 600 seconds after the first attempt, which cuts the last wait short; the manifest cannot change that limit. Each stream's `$parameters.required_ability` is the *Ability Requirements* column of its object page, without the word "ability". The version 4 page behind `email_clicks` names none, so its code 49 message asks for "View".

**Why this matters:** A filter on the HTTP status would miss a code the vendor sends with another status. A new stream needs a `required_ability`, or its code 49 message cannot say what to ask for.

## 2. The Daily Limit Ends the Sync

Each account gets a daily number of requests by edition (Growth 25,000; Plus 50,000; Advanced and Premium 100,000), and "These limits reset at the beginning of the day based on your account time zone settings" ([Rate limits](https://developer.salesforce.com/docs/marketing/pardot/guide/overview.html)). A retry cannot succeed before then, and a wait of hours would pass the platform's heartbeat (`maxSecondsBetweenMessages: 3600`). The sync fails at once as a transient error, and the next sync continues from the saved state.

**Why this matters:** Before 1.1.0 every retryable answer waited two hours, longer than the platform lets a sync stay silent.

## 3. No API Budget

The manifest declares no `api_budget`. The daily limit depends on the customer's edition and is shared with their other integrations, so a fixed budget would either throttle a large account or not protect a small one. The limit of five concurrent requests is held by `concurrency_level`: `num_workers` from 2 to 5, 3 by default, and `max_concurrency: 5`. Code 122 and code 66 are handled in section 1.

**Why this matters:** A `max_concurrency` above five lets the connector send more concurrent requests than the vendor allows.

## 4. One Login at a Time, and the Host Follows the Account Type

The login is the CDK's `OAuthAuthenticator` with a refresh-token grant at `login.salesforce.com`, or `test.salesforce.com` when `is_sandbox` is on. Each stream keeps its own token, so a sync logs in once per stream, but the CDK holds one lock for every token refresh: no two token requests are in flight at once. Salesforce rejects a parallel one with `token request is already being processed`; that answer is not retried. When the token answer carries no `expires_in`, the CDK keeps the token for one hour. `expired access/refresh token` fails as a configuration error that says to create a new refresh token.

The API host is `pi.pardot.com` for production, `pi.demo.pardot.com` for a sandbox and for a Developer Edition org ([Authentication](https://developer.salesforce.com/docs/marketing/pardot/guide/authentication.html)). A Developer Edition org signs in at `login.salesforce.com`, so it needs `pardot_api_host: pi.demo.pardot.com`. `pardot_api_host` is an `enum` of the two hosts, so `allowedHosts` stays a fixed list of four and a config cannot send the token elsewhere. A test fails when a read sends a request to a host that `allowedHosts` does not list.

**Why this matters:** Before 1.1.0 two streams could log in at once and fail the sync, and sandbox accounts could not connect.

## 5. The Restart After 100,000 Records

Version 5 pages follow `nextPageUrl`, which carries only `fields` and the page token, as the vendor requires. "The pagination feature has a limit of 100,000 records. When a query reaches the limit it doesn't generate a new nextPageToken" ([Version 5 overview](https://developer.salesforce.com/docs/marketing/pardot/guide/version5overview.html)). When a full page of 1,000 comes back without `nextPageUrl`, the 20 version 5 incremental streams other than `visitors` start a new query from the last record's cursor with the inclusive `...AfterOrEqualTo` filter of their cursor field, sent once and percent-encoded. The same filter carries the saved cursor between syncs. The full-refresh streams restart on `idGreaterThan`, and ids are unique.

The new query reads the records of the boundary second again, which adds duplicates for destinations that append. Known limit: if 100,000 records share one second, the restart repeats the same query and cannot advance.

**Why this matters:** The exclusive `...After` filter skipped every record that shared its second with the last one read.

## 6. What Waits for a Test Account

- `visitors` filters on `updatedAtAfter`, which the vendor's filter table for that object does not list in either form ([Visitor](https://developer.salesforce.com/docs/marketing/pardot/guide/visitor-v5.html)). It is unchanged until a live request shows what the API does with it.
- The version 5 incremental streams write their cursor with a literal `-12:00` (`datetime_format: "%Y-%m-%dT%H:%M:%S-12:00"`), and the first sync saves the start date rather than the newest cursor. Whether the API reads that offset needs one live request; a change may need a state migration.
- `email_clicks` filters on `created_after`, which the vendor describes as "created after the specified time". A record of the saved second can be skipped. A one-second `lookback_window` would re-read that second on every sync.

**Why this matters:** These are known gaps, not oversights. Change them only with a live read to compare against.

## 7. Saved Configs Are Cleaned

`spec.config_normalization_rules` removes `v5_page_size`, `page_size` and `split_up_interval` from saved configs. `split_up_interval` was removed from the spec in 1.0.1, `page_size` was replaced by `v5_page_size` in 1.0.25, and nothing read `v5_page_size` before it was removed in 1.1.0.

**Why this matters:** The earlier spec changes shipped without a migration, and one of them broke a Terraform setup ([airbyte#68192](https://github.com/airbytehq/airbyte/issues/68192)).
