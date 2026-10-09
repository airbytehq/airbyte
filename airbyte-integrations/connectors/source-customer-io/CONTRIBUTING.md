# Contributing to source-customer-io

For general guidance on contributing to Airbyte connectors, see the
[Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Unique behaviors (summary)

Full technical detail for each item lives in [AGENTS.md](./AGENTS.md).

1. **The App API Is API-Key-Only** - every request sends the App API key as a bearer token.
   Customer.io offers OAuth only for its MCP server ([auth.md](https://docs.customer.io/auth.md)),
   so there is no OAuth flow to add. A wrong Region fails with 401 like an invalid key
   ([data centers](https://docs.customer.io/accounts/settings/data-centers/#specifying-your-region-in-the-api)).
   Details in AGENTS.md section 1.
2. **HTTP Errors Are Classified on the Shared Base Requester** - 401 and 403 fail as configuration
   errors that name the fix; 429 waits for `Retry-After`
   ([API rate limits](https://docs.customer.io/integrations/api/customerio-apis/#api-rate-limits)),
   or backs off exponentially when the header is absent, for at most 30 retries; 5xx retry; a 404
   on a substream request (its parent automation, broadcast, one-time send or segment was deleted
   mid-sync) skips that parent's records; anything else follows the CDK default mapping. Details in AGENTS.md section 2.
3. **One Shared Request Budget and Three Workers** - `api_budget` allows 10 requests per second
   ([rate limits](https://docs.customer.io/integrations/api/app/#rate-limits)), the App API limit
   shared by the whole workspace (`components.responses.InboxPreviewReadRateLimited` in the
   [OpenAPI spec](https://docs.customer.io/files/journeys-app.json)), and `concurrency_level` runs
   3 workers. Substreams send one request per parent record. Details in AGENTS.md section 3.
4. **Incremental Sync Is Client-Side With a One-Hour Lookback, Except `messages`** - only
   `listMessages` filters by time ([OpenAPI spec](https://docs.customer.io/files/journeys-app.json)),
   so `messages` reads server-side windows (item 17); every other incremental stream reads its
   full list and keeps records whose `updated`, `updated_at` or `timestamp` (epoch seconds) is at or after the saved
   cursor minus one hour, so Incremental | Append stores the last hour's records again on every
   sync. `activities` stops at the first page with no activity in that window, which relies on its
   newest-first order (item 18). A new campaign's or broadcast's actions start from the
   stream-wide cursor, not the Start Date. `newsletter_variants`, `sender_identities`,
   `segment_usage`, `subscription_topics`, `object_types`, `workspaces` and `reporting_webhooks`
   are full refresh: the spec documents no update-time field for them (variants return an
   undocumented `updated`, see AGENTS.md section 4), and full refresh also drops deleted records. So are `people`,
   `segment_memberships` and `esp_suppressions`: profiles and memberships have no update time, a
   suppression only its creation time, and people who leave a segment and lifted suppressions
   disappear without a record. `collections` is full refresh as well (item 16). Details in AGENTS.md
   section 4.
5. **Substream Parents Are Inline Copies Without a Cursor** - the parent list each substream reads
   ignores Start Date on purpose, because a parent last updated before Start Date can still have
   child records that changed later. Details in AGENTS.md section 5.
6. **Action IDs May Arrive as JSON Strings** - `campaigns_actions.id` is a JSON string although the
   [OpenAPI spec](https://docs.customer.io/files/journeys-app.json) documents an integer, so joins
   with `campaigns.actions[].id` need a cast; `broadcast_actions` casts its `id` to the documented
   integer. `from_id` and `reply_to_id` are integers, as documented. Details in AGENTS.md section 6.
7. **Language and A/B Variants Are Separate Records** - `broadcast_actions` has one record per
   language variant of a message
   ([broadcastActions](https://docs.customer.io/integrations/api/app/tag/broadcasts/broadcastactions/)),
   and `newsletter_variants` one per language or A/B test of a one-time send
   ([listNewsletterVariants](https://docs.customer.io/integrations/api/app/tag/newsletter-variants/listnewslettervariants/)),
   each with its own `id`. Details in AGENTS.md section 7.
8. **`sender_identities` Reads Visible and Hidden Senders and Ends on an Empty Page** - `hidden=true`
   leaves visible senders out, so the stream reads the `hidden=false` and `hidden=true` lists and
   keeps each sender only in the list its own flag belongs to
   ([listSenders](https://docs.customer.io/integrations/api/app/tag/sender-identities/listsenders/)),
   and each list ends with one request that returns no senders, because the API returns a
   next-page token after the last one. Details in AGENTS.md section 8.
9. **Archived Segments Are Not Synced** - Customer.io leaves archived segments out of the segment
   list ([listSegments](https://docs.customer.io/integrations/api/app/tag/segments/listsegments/)),
   so `segments`, `segment_usage` and `segment_memberships` skip them; `segment_usage` has one
   record per listed segment.
   Details in AGENTS.md section 9.
10. **`campaigns_actions` Logs a Harmless Parent-State Warning** - "Parent state handling is not
    supported for CartesianProductStreamSlicer." comes from the one-element `partition_router` list
    and needs no action. Details in AGENTS.md section 10.
11. **Four `campaigns` Fields Are Untyped** - `audience.person_filters`,
    `audience.relationship_filters`, `object_attribute_triggers` and
    `relationship_attribute_triggers` are typed `object` in the
    [OpenAPI spec](https://docs.customer.io/files/journeys-app.json), but every example there is a
    JSON string and no live record shows them, so the schema leaves them untyped. Details in
    AGENTS.md section 11.
12. **`subscription_topics` Is Empty Until Topics Are Added** - the list is empty when the workspace
    has no topics ([getTopics](https://docs.customer.io/integrations/api/app/tag/subscription-center/gettopics/)),
    as in the test workspace. Topics exist before the subscription center can be enabled
    ([enable the subscription center](https://docs.customer.io/messaging/channels/subscriptions/center/#enable-sub-center)),
    so a non-empty stream does not mean the center is on. Details in AGENTS.md section 12.
13. **`workspaces` Is a Snapshot of Account-Wide Counts** - every workspace in the account, not
    only the key's, with message counts for the current billing period and current people and
    object totals, cached for up to two hours
    ([listWorkspaces](https://docs.customer.io/integrations/api/app/tag/workspaces/listworkspaces/)).
    The records have no update time, so only full refresh is meaningful. Details in AGENTS.md
    section 13.
14. **`reporting_webhooks.endpoint` Can Carry Credentials** - the connector removes the
    `username:password@` part Customer.io documents for securing a reporting webhook
    ([reporting webhooks FAQ](https://docs.customer.io/integrations/data-out/connections/webhooks/#frequently-asked-questions)),
    but a token in the path or query string is synced as returned, so the stream is not in
    `suggestedStreams`; connections that propagate all field and stream changes still add it after
    the upgrade. Details in AGENTS.md section 14.
15. **`snippets` Are Keyed by Name** - snippets have no ID, and their names are unique and cannot
    change ([snippets FAQ](https://docs.customer.io/messaging/liquid/snippets/#frequently-asked-questions)),
    so `name` is the primary key. Details in AGENTS.md section 15.
16. **`collections` Lists Metadata, Not Contents** - names, row keys, row counts and sizes
    ([getCollections](https://docs.customer.io/integrations/api/app/tag/collections/getcollections/)),
    full refresh only, because a contents change may not move `updated_at`; the connector never calls
    [getCollectionContents](https://docs.customer.io/integrations/api/app/tag/collections/getcollectioncontents/).
    Details in AGENTS.md section 16.
17. **`messages` Reads 30-Day Windows of Creation Time and Re-Reads a Lookback** - one record per
    delivery, read in server-side windows of creation time
    ([listMessages](https://docs.customer.io/integrations/api/app/tag/messages/listmessages/)).
    Metrics keep arriving after creation (opens and clicks for 6 months, conversions for up to 90
    days), so each sync re-reads the deliveries of the last `messages_lookback_days` (default 30),
    one request per 1,000. A deleted person's deliveries keep only `cio_id`, but rows synced before
    keep the address. Details in AGENTS.md section 17.
18. **`activities` Holds 30 Days and Stops at the First Page Outside the Cursor Window** - the API
    guarantees only 30 days of history and has no time filter
    ([listActivities](https://docs.customer.io/integrations/api/app/tag/activities/listactivities/)),
    so the read stops at the first page with no activity in the cursor window. That relies on the
    newest-first order by `timestamp` seen live, so a block of backdated events can hide newer
    ones. Every request sends `deleted=true`, and a page of only future-dated activities does not
    stop the read. Details in AGENTS.md section 18.
19. **`people` Searches Every Profile, Then Fetches 100 at a Time** - a search for everyone with a
    `cio_id` ([getPeopleFilter](https://docs.customer.io/integrations/api/app/tag/customers/getpeoplefilter/))
    lists every person, and
    [getPeopleById](https://docs.customer.io/integrations/api/app/tag/customers/getpeoplebyid/)
    fetches 100 profiles per request, so a sync costs ceil(N/1000) + ceil(N/100) requests. The
    fetch omits unknown IDs without an error, and its items are not wrapped in `customer` as the
    spec shows, so check the record count, not only the status. Every field is personal data.
    Details in AGENTS.md section 19.
20. **`segment_memberships` Has One Row per Person per Segment** - the sum of all segment sizes,
    read 30,000 members per request
    ([getSegmentMembership](https://docs.customer.io/integrations/api/app/tag/segments/getsegmentmembership/)),
    full refresh only; members of a segment whose `state` is `build` can be out of date. Details in
    AGENTS.md section 20.
21. **`esp_suppressions` Reads Each Suppression List per Sending Domain** - four suppression types
    crossed with the optional `esp_suppression_domains`, paged by offset until a short or null page
    ([getSuppressionByType](https://docs.customer.io/integrations/api/app/tag/esp-suppression/getsuppressionbytype/)).
    Only Customer.io's own email service provider keeps these lists, and the rows are end-user email
    addresses. Details in AGENTS.md section 21.
22. **The Personal-Data Streams Stay Out of `suggestedStreams`** - the five streams of items 17 to
    21 carry end-user data, so new connections leave them unselected; connections that propagate all
    field and stream changes still add them on upgrade. Details in AGENTS.md section 22.

## Testing notes

- From the connector directory, `poe test-unit-tests` runs the requests-mock tests in
  `unit_tests/`, and `airbyte-cdk connector test` runs the standard tests against
  `secrets/config.json`.
- `integration_tests/invalid_config.json` holds an invalid key with a past Start Date, so the
  failed check exercises the 401 message. There is no `expected_records.jsonl`: the sandbox data
  changes and no current harness asserts on it.
- `broadcasts` and `broadcast_actions` are `empty_streams` in `acceptance-test-config.yml`: the test
  workspace has no API-triggered broadcasts, and the App API cannot create one, so only the unit
  tests read them.
- `subscription_topics` and `object_types` are also `empty_streams`: the test workspace has
  neither, and the App API cannot create them, so only the unit tests read them.
- `activities` returns only about the last 30 days, so it goes empty after 30 days without activity
  in the test workspace: add some (for example, open a test email) or list it under
  `empty_streams`.
- Keep live responses out of fixtures: `messages`, `activities`, `people`, `segment_memberships`
  and `esp_suppressions` return real email addresses, and the suppression lists hold third-party
  ones.
