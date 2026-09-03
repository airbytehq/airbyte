# Greenhouse

This page contains the setup guide and reference information for the Greenhouse source connector.

## Prerequisites

The connector authenticates to Greenhouse Harvest v3 with OAuth 2.0 Authorization Code through Airbyte's registered Greenhouse partner application. You don't create, request, or register a Greenhouse OAuth application of your own: Greenhouse issues Harvest v3 partner credentials only to integration partners, not to Greenhouse customers, and doesn't permit customers to connect through their own applications. Airbyte supplies the client ID and client secret during the consent flow.

To set up the source, you need:

- An Airbyte Cloud workspace. The consent flow relies on Airbyte's partner credentials, which are only available in Airbyte Cloud.
- A Greenhouse user who is a Site Admin to approve the consent flow.

The consent flow requests these scopes; approve all of them:

- `harvest:applications:list`
- `harvest:approval_flows:list`
- `harvest:candidate_tags:list`
- `harvest:candidates:list`
- `harvest:close_reasons:list`
- `harvest:custom_field_options:list`
- `harvest:custom_fields:list`
- `harvest:demographic_answer_options:list`
- `harvest:demographic_answers:list`
- `harvest:demographic_question_sets:list`
- `harvest:demographic_questions:list`
- `harvest:departments:list`
- `harvest:eeoc:list`
- `harvest:email_templates:list`
- `harvest:interviews:list`
- `harvest:job_interview_stages:list`
- `harvest:job_posts:list`
- `harvest:jobs:list`
- `harvest:notes:list`
- `harvest:offers:list`
- `harvest:offices:list`
- `harvest:openings:list`
- `harvest:prospect_pools:list`
- `harvest:rejection_reasons:list`
- `harvest:scorecards:list`
- `harvest:sources:list`
- `harvest:user_job_permissions:list`
- `harvest:user_roles:list`
- `harvest:users:list`

Harvest v3 rejects requests to its list endpoints from any user who isn't a Site Admin, and the connector fails the sync with a configuration error. A missing scope produces the same failure for the streams that depend on it, so grant every scope in the list unless you plan to leave the corresponding streams disabled. Grant `harvest:users:list` in every case: the connection check reads the `users` stream, so the source fails to set up without it even if you never sync that stream.

## Set up the Greenhouse connector in Airbyte

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Greenhouse** from the Source type dropdown.
4. Enter the name for the Greenhouse connector.
5. Click **Authenticate**, sign in to Greenhouse as a Site Admin, and approve the requested scopes. Airbyte fills in its partner application's client ID and client secret and stores the resulting refresh token. You don't enter any Greenhouse credentials yourself.
6. Optionally enter a **Start date** in UTC using the format `YYYY-MM-DDTHH:MM:SSZ`. Records updated before this date will not be replicated. If omitted, the connector replicates all history.
7. Optionally change **Number of concurrent threads**. The connector syncs with 2 threads by default and accepts 1 to 8. All threads share one Greenhouse rate limit, so raise this only if your Greenhouse account can absorb more API traffic, and lower it to 1 if syncs fail with rate-limit errors.
8. Click **Set up source**.

:::warning
Greenhouse refresh tokens expire after approximately 24 hours of non-use and rotate on every refresh. Set connections to sync more often than once a day. A connection left paused, turned off, or failing for more than 24 hours requires re-running the consent flow from the source settings. See [Troubleshooting](#troubleshooting) for the error this produces.
:::

## Supported sync modes

The Greenhouse source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
- [Incremental - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
- [Incremental - Append + Deduped](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append-deduped)

## Supported Streams

The table lists the stream names as they appear in Airbyte, with the Harvest v3 endpoint each one reads. **Start date** applies only to the incremental streams. Full refresh streams always read everything the endpoint returns, and the five child streams pull parent IDs over your full Greenhouse history, so their coverage doesn't depend on **Start date** either. `demographics_answer_options`, `demographics_questions`, and `demographics_question_sets` are full refresh because Harvest v3 exposes no date filter on those endpoints.

| Stream | Sync mode | Notes |
| :--- | :--- | :--- |
| [`activity_feed`](https://harvestdocs.greenhouse.io/reference/get_v3-notes) | Full refresh | Notes for each candidate in `candidates` |
| [`applications`](https://harvestdocs.greenhouse.io/reference/get_v3-applications) | Incremental (`updated_at`) | |
| [`approvals`](https://harvestdocs.greenhouse.io/reference/get_v3-approval-flows) | Full refresh | |
| [`candidates`](https://harvestdocs.greenhouse.io/reference/get_v3-candidates) | Incremental (`updated_at`) | |
| [`close_reasons`](https://harvestdocs.greenhouse.io/reference/get_v3-close-reasons) | Full refresh | |
| [`custom_field_options`](https://harvestdocs.greenhouse.io/reference/get_v3-custom-field-options) | Full refresh | Every custom field option in the account |
| [`custom_fields`](https://harvestdocs.greenhouse.io/reference/get_v3-custom-fields) | Full refresh | |
| [`degrees`](https://harvestdocs.greenhouse.io/reference/get_v3-custom-field-options) | Full refresh | Custom field options for the `degree` field |
| [`demographics_answer_options`](https://harvestdocs.greenhouse.io/reference/get_v3-demographic-answer-options) | Full refresh | |
| [`demographics_answers`](https://harvestdocs.greenhouse.io/reference/get_v3-demographic-answers) | Incremental (`updated_at`) | |
| [`demographics_answers_answer_options`](https://harvestdocs.greenhouse.io/reference/get_v3-demographic-answer-options) | Full refresh | Answer options for each question in `demographics_questions` |
| [`demographics_question_sets`](https://harvestdocs.greenhouse.io/reference/get_v3-demographic-question-sets) | Full refresh | |
| [`demographics_question_sets_questions`](https://harvestdocs.greenhouse.io/reference/get_v3-demographic-questions) | Full refresh | Questions in each set in `demographics_question_sets` |
| [`demographics_questions`](https://harvestdocs.greenhouse.io/reference/get_v3-demographic-questions) | Full refresh | |
| [`departments`](https://harvestdocs.greenhouse.io/reference/get_v3-departments) | Full refresh | |
| [`disciplines`](https://harvestdocs.greenhouse.io/reference/get_v3-custom-field-options) | Full refresh | Custom field options for the `discipline` field |
| [`eeoc`](https://harvestdocs.greenhouse.io/reference/get_v3-eeoc) | Incremental (`submitted_at`) | |
| [`email_templates`](https://harvestdocs.greenhouse.io/reference/get_v3-email-templates) | Incremental (`updated_at`) | |
| [`interviews`](https://harvestdocs.greenhouse.io/reference/get_v3-interviews) | Incremental (`updated_at`) | |
| [`job_posts`](https://harvestdocs.greenhouse.io/reference/get_v3-job-posts) | Incremental (`updated_at`) | Includes deleted posts |
| [`job_stages`](https://harvestdocs.greenhouse.io/reference/get_v3-job-interview-stages) | Incremental (`updated_at`) | |
| [`jobs`](https://harvestdocs.greenhouse.io/reference/get_v3-jobs) | Incremental (`updated_at`) | |
| [`jobs_openings`](https://harvestdocs.greenhouse.io/reference/get_v3-openings) | Full refresh | Openings for each job in `jobs` |
| [`offers`](https://harvestdocs.greenhouse.io/reference/get_v3-offers) | Incremental (`updated_at`) | |
| [`offices`](https://harvestdocs.greenhouse.io/reference/get_v3-offices) | Full refresh | |
| [`prospect_pools`](https://harvestdocs.greenhouse.io/reference/get_v3-prospect-pools) | Full refresh | |
| [`rejection_reasons`](https://harvestdocs.greenhouse.io/reference/get_v3-rejection-reasons) | Full refresh | Includes the reasons Greenhouse ships with |
| [`schools`](https://harvestdocs.greenhouse.io/reference/get_v3-custom-field-options) | Full refresh | Custom field options for the `school_name` field |
| [`scorecards`](https://harvestdocs.greenhouse.io/reference/get_v3-scorecards) | Incremental (`updated_at`) | |
| [`sources`](https://harvestdocs.greenhouse.io/reference/get_v3-sources) | Full refresh | |
| [`tags`](https://harvestdocs.greenhouse.io/reference/get_v3-candidate-tags) | Full refresh | Candidate tags |
| [`user_permissions`](https://harvestdocs.greenhouse.io/reference/get_v3-user-job-permissions) | Full refresh | Job permissions for each user in `users` |
| [`user_roles`](https://harvestdocs.greenhouse.io/reference/get_v3-user-roles) | Full refresh | |
| [`users`](https://harvestdocs.greenhouse.io/reference/get_v3-users) | Incremental (`updated_at`) | Includes integration service users |

## Performance considerations

Greenhouse [rate limits](https://harvestdocs.greenhouse.io/docs/api-rate-limiting) Harvest v3 in fixed 30-second windows. Each response reports your remaining allowance in `X-RateLimit-Remaining` and the time the current window resets in `X-RateLimit-Reset`. Greenhouse doesn't publish a fixed request ceiling for Harvest v3, and it applies different allowances to custom and partner integrations, so the connector holds itself to a conservative 50 requests per window, tracks those headers, and waits for the `Retry-After` interval when Greenhouse returns `429`. Because every thread draws on the same window, syncing many streams at a high **Number of concurrent threads** is a common cause of rate-limit errors. Lower that value before [creating an issue](https://github.com/airbytehq/airbyte/issues) about rate limits.

The connector requests 500 records per page, the Harvest v3 maximum, and then follows the cursor links Greenhouse returns, so large accounts still page through many requests per stream.

## Limitations

- **`job_posts`** includes job posts that were deleted in Greenhouse. Harvest v3 excludes deleted posts by default, and the connector requests both active and deleted posts. Filter on `active` downstream if you only want live posts.
- **`eeoc`** replicates on `submitted_at`. A correction to an EEOC response after submission doesn't change `submitted_at`, so incremental syncs never re-read it. Refresh the stream if you need corrections to land.
- **`custom_field_options`** reads every custom field option in your account, which makes it a superset of `degrees`, `disciplines`, and `schools`. Those three streams read the same Greenhouse endpoint filtered to one field key and share the same primary keys, so enabling all four writes the same option rows to four destination tables. Enable only the ones you need.
- **`users`** includes integration service users, which Greenhouse hides by default. Service accounts have no email address, so `primary_email` is empty for those records.
- **`rejection_reasons`** includes the default reasons Greenhouse ships with, not only the ones your organization added.

## Troubleshooting

### Sync fails with a configuration error asking you to re-authenticate

The connector can't renew its access token because Greenhouse rejected the refresh token. Starting with version 1.0.1, the connector reports this as a configuration error instead of a system error. The Greenhouse error code in the sync log tells you what to fix:

- `invalid_grant`: the refresh token expired or was invalidated. This happens when the connection hasn't synced for more than about 24 hours, or when another tool used the same refresh token, which causes Greenhouse to issue a new one that Airbyte never receives. Open the source settings, click **Authenticate**, and complete the consent flow again to store a new refresh token. Run the consent flow separately for each Airbyte source; don't reuse one refresh token across sources or other tools.
- `invalid_client` or `unauthorized_client`: Greenhouse rejected the partner application credentials Airbyte used for the refresh, or that application isn't allowed to use the refresh token grant. Open the source settings, click **Authenticate**, and complete the consent flow again. If the error persists, contact Airbyte support; there are no credentials for you to correct on your side.

### Sync fails with a `403` configuration error on a stream

The authorizing user isn't a Site Admin, or the consent flow didn't include the scope for that stream. Compare the scopes in [Prerequisites](#prerequisites) with the ones you approved, then re-run the consent flow as a Site Admin.

## Migration from Harvest v1 before the v1/v2 sunset

Version 1.0.0 migrates the 33 streams carried over from 0.8.1 from Harvest v1 to Harvest v3 and adds the new `custom_field_options` stream, for 34 streams in total, because Greenhouse has scheduled the end of support for Harvest v1 and v2 together on 2026-08-31. It also replaces API-key authentication with OAuth Authorization Code authentication for every deployment and introduces an optional **Start date** that preserves the previous full-history behavior when omitted. We recommend creating a new connection on 1.0.0 rather than refreshing the existing one; see the [upgrade paths](./greenhouse-migrations.md#upgrade-paths) before upgrading.

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version    | Date       | Pull Request                                             | Subject                                                                                                                                                                |
|:-----------|:-----------|:---------------------------------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1.0.2 | 2026-09-02 | [85306](https://github.com/airbytehq/airbyte/pull/85306) | Clarify in the spec that OAuth credentials come from Airbyte's Greenhouse partner application and must not be requested from Greenhouse |
| 1.0.1 | 2026-09-02 | [85300](https://github.com/airbytehq/airbyte/pull/85300) | Surface expired or rotated refresh tokens (`invalid_grant`) as a re-authenticate config error instead of a system error |
| 1.0.0 | 2026-08-28 | [84846](https://github.com/airbytehq/airbyte/pull/84846) | Breaking migration from Harvest v1 to Harvest v3 with OAuth. See the [migration guide](https://docs.airbyte.com/integrations/sources/greenhouse-migrations). |
| 0.8.1 | 2026-08-18 | [84641](https://github.com/airbytehq/airbyte/pull/84641) | Update dependencies |
| 0.8.0 | 2026-08-12 | [83811](https://github.com/airbytehq/airbyte/pull/83811) | Send pagination page-size parameters only on first-page requests and use fully-qualified per-stream URLs in preparation for the Harvest v3 migration. |
| 0.7.33 | 2026-08-11 | [83956](https://github.com/airbytehq/airbyte/pull/83956) | Update dependencies |
| 0.7.32 | 2026-07-28 | [83194](https://github.com/airbytehq/airbyte/pull/83194) | Update to CDK 7.23.8 (fixes AirbyteCustomCodeNotPermittedError for bundled custom components) and remove the temporary Cloud version override |
| 0.7.31 | 2026-07-28 | [1082](https://github.com/airbytehq/airbyte-python-cdk/issues/1082) | Roll Cloud back to 0.7.29 — 0.7.30 is built on SDM 7.23.7, which breaks bundled custom components |
| 0.7.30 | 2026-07-28 | [82944](https://github.com/airbytehq/airbyte/pull/82944) | Update dependencies |
| 0.7.29 | 2026-07-21 | [82444](https://github.com/airbytehq/airbyte/pull/82444) | Update dependencies |
| 0.7.28 | 2026-07-14 | [81887](https://github.com/airbytehq/airbyte/pull/81887) | Update dependencies |
| 0.7.27 | 2026-06-30 | [81129](https://github.com/airbytehq/airbyte/pull/81129) | Update dependencies |
| 0.7.26 | 2026-06-23 | [80487](https://github.com/airbytehq/airbyte/pull/80487) | Update dependencies |
| 0.7.25 | 2026-06-16 | [79888](https://github.com/airbytehq/airbyte/pull/79888) | Update dependencies |
| 0.7.24 | 2026-06-09 | [79354](https://github.com/airbytehq/airbyte/pull/79354) | Update dependencies |
| 0.7.23 | 2026-06-02 | [78766](https://github.com/airbytehq/airbyte/pull/78766) | Update dependencies |
| 0.7.22 | 2026-05-15 | [78119](https://github.com/airbytehq/airbyte/pull/78119) | Set the default concurrency to 2 and expose the number of concurrent threads as a user-configurable option. |
| 0.7.22-rc.3 | 2026-05-12 | [78052](https://github.com/airbytehq/airbyte/pull/78052) | Reduce default_concurrency to 3 for concurrency tuning after rate-limit failures at higher settings. |
| 0.7.22-rc.2 | 2026-05-08 | [78006](https://github.com/airbytehq/airbyte/pull/78006) | Concurrency tuning iteration: bump default_concurrency to 5 |
| 0.7.22-rc.1 | 2026-05-06 | [77826](https://github.com/airbytehq/airbyte/pull/77826) | Start concurrency tuning at default_concurrency=4 (Path A) and enable progressive rollout |
| 0.7.21 | 2026-04-28 | [77287](https://github.com/airbytehq/airbyte/pull/77287) | Update dependencies |
| 0.7.20 | 2026-04-21 | [76637](https://github.com/airbytehq/airbyte/pull/76637) | Update dependencies |
| 0.7.19 | 2026-03-31 | [75729](https://github.com/airbytehq/airbyte/pull/75729) | Update dependencies |
| 0.7.18 | 2026-03-17 | [74919](https://github.com/airbytehq/airbyte/pull/74919) | Update dependencies |
| 0.7.17 | 2026-03-10 | [74688](https://github.com/airbytehq/airbyte/pull/74688) | Update dependencies |
| 0.7.16 | 2026-03-03 | [74176](https://github.com/airbytehq/airbyte/pull/74176) | Update dependencies |
| 0.7.15 | 2026-02-10 | [73107](https://github.com/airbytehq/airbyte/pull/73107) | Update dependencies |
| 0.7.14 | 2026-02-03 | [72661](https://github.com/airbytehq/airbyte/pull/72661) | Update dependencies |
| 0.7.13 | 2026-01-20 | [71894](https://github.com/airbytehq/airbyte/pull/71894) | Update dependencies |
| 0.7.12 | 2026-01-14 | [71700](https://github.com/airbytehq/airbyte/pull/71700) | Update dependencies |
| 0.7.11 | 2025-12-18 | [70503](https://github.com/airbytehq/airbyte/pull/70503) | Update dependencies |
| 0.7.10 | 2025-11-25 | [70056](https://github.com/airbytehq/airbyte/pull/70056) | Update dependencies |
| 0.7.9 | 2025-11-18 | [69420](https://github.com/airbytehq/airbyte/pull/69420) | Update dependencies |
| 0.7.8 | 2025-10-29 | [68823](https://github.com/airbytehq/airbyte/pull/68823) | Update dependencies |
| 0.7.7 | 2025-10-21 | [68226](https://github.com/airbytehq/airbyte/pull/68226) | Update dependencies |
| 0.7.6 | 2025-10-14 | [67896](https://github.com/airbytehq/airbyte/pull/67896) | Update dependencies |
| 0.7.5 | 2025-10-07 | [67399](https://github.com/airbytehq/airbyte/pull/67399) | Update dependencies |
| 0.7.4 | 2025-09-30 | [66408](https://github.com/airbytehq/airbyte/pull/66408) | Update dependencies |
| 0.7.3 | 2025-09-09 | [65896](https://github.com/airbytehq/airbyte/pull/65896) | Update dependencies |
| 0.7.2 | 2025-08-28 | [64973](https://github.com/airbytehq/airbyte/pull/64973) | Update dependencies |
| 0.7.1 | 2025-08-26 | [65510](https://github.com/airbytehq/airbyte/pull/65510) | Fix custom migrations to reference DeclarativeStream Pydantic model instead of runtime component |
| 0.7.0 | 2025-07-07 | [62830](https://github.com/airbytehq/airbyte/pull/62830) | Promoting release candidate 0.7.0-rc.1 to a main version. |
| 0.7.0-rc.1 | 2025-06-29 | [47283](https://github.com/airbytehq/airbyte/pull/47283) | Migrate to Manifest-only |
| 0.6.1 | 2025-03-22 | [53800](https://github.com/airbytehq/airbyte/pull/53800) | Update dependencies |
| 0.6.0 | 2025-03-14 | [55774](https://github.com/airbytehq/airbyte/pull/55774) | Promoting release candidate 0.6.0-rc.1 to a main version. |
| 0.6.0-rc.1 | 2025-03-14 | [54702](https://github.com/airbytehq/airbyte/pull/54702) | Update to latest airbyte-cdk, remove custom cursors. |
| 0.5.32 | 2025-02-01 | [52724](https://github.com/airbytehq/airbyte/pull/52724) | Update dependencies |
| 0.5.31 | 2025-01-25 | [51842](https://github.com/airbytehq/airbyte/pull/51842) | Update dependencies |
| 0.5.30 | 2025-01-11 | [51214](https://github.com/airbytehq/airbyte/pull/51214) | Update dependencies |
| 0.5.29 | 2024-12-28 | [50632](https://github.com/airbytehq/airbyte/pull/50632) | Update dependencies |
| 0.5.28 | 2024-12-21 | [50109](https://github.com/airbytehq/airbyte/pull/50109) | Update dependencies |
| 0.5.27 | 2024-12-14 | [49248](https://github.com/airbytehq/airbyte/pull/49248) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.5.26 | 2024-12-12 | [48996](https://github.com/airbytehq/airbyte/pull/48996) | Update dependencies |
| 0.5.25 | 2024-10-29 | [47110](https://github.com/airbytehq/airbyte/pull/47110) | Update dependencies |
| 0.5.24 | 2024-10-23 | [47306](https://github.com/airbytehq/airbyte/pull/47306) | Add 'job_post_id' to applications stream scehma |
| 0.5.23 | 2024-10-12 | [46828](https://github.com/airbytehq/airbyte/pull/46828) | Update dependencies |
| 0.5.22 | 2024-10-05 | [46506](https://github.com/airbytehq/airbyte/pull/46506) | Update dependencies |
| 0.5.21 | 2024-09-28 | [46159](https://github.com/airbytehq/airbyte/pull/46159) | Update dependencies |
| 0.5.20 | 2024-09-21 | [45834](https://github.com/airbytehq/airbyte/pull/45834) | Update dependencies |
| 0.5.19 | 2024-09-17 | [45625](https://github.com/airbytehq/airbyte/pull/45625) | Change check stream |
| 0.5.18 | 2024-09-14 | [45476](https://github.com/airbytehq/airbyte/pull/45476) | Update dependencies |
| 0.5.17 | 2024-09-07 | [45229](https://github.com/airbytehq/airbyte/pull/45229) | Update dependencies |
| 0.5.16 | 2024-08-31 | [44755](https://github.com/airbytehq/airbyte/pull/44755) | Update dependencies |
| 0.5.15 | 2024-08-17 | [44246](https://github.com/airbytehq/airbyte/pull/44246) | Update dependencies |
| 0.5.14 | 2024-08-10 | [43595](https://github.com/airbytehq/airbyte/pull/43595) | Update dependencies |
| 0.5.13 | 2024-08-03 | [43160](https://github.com/airbytehq/airbyte/pull/43160) | Update dependencies |
| 0.5.12 | 2024-07-27 | [42816](https://github.com/airbytehq/airbyte/pull/42816) | Update dependencies |
| 0.5.11 | 2024-07-20 | [42240](https://github.com/airbytehq/airbyte/pull/42240) | Update dependencies |
| 0.5.10 | 2024-07-13 | [41787](https://github.com/airbytehq/airbyte/pull/41787) | Update dependencies |
| 0.5.9 | 2024-07-10 | [41215](https://github.com/airbytehq/airbyte/pull/41215) | Update dependencies |
| 0.5.8 | 2024-07-10 | [39601](https://github.com/airbytehq/airbyte/pull/39601) | Move spec to manifest, fix readme |
| 0.5.7 | 2024-07-06 | [40882](https://github.com/airbytehq/airbyte/pull/40882) | Update dependencies |
| 0.5.6 | 2024-06-25 | [40451](https://github.com/airbytehq/airbyte/pull/40451) | Update dependencies |
| 0.5.5 | 2024-06-22 | [39968](https://github.com/airbytehq/airbyte/pull/39968) | Update dependencies |
| 0.5.4 | 2024-06-06 | [39247](https://github.com/airbytehq/airbyte/pull/39247) | [autopull] Upgrade base image to v1.2.2 |
| 0.5.3 | 2024-04-19 | [36640](https://github.com/airbytehq/airbyte/pull/36640) | Updating to 0.80.0 CDK |
| 0.5.2 | 2024-04-12 | [36640](https://github.com/airbytehq/airbyte/pull/36640) | schema descriptions |
| 0.5.1 | 2024-03-12 | [35988](https://github.com/airbytehq/airbyte/pull/35988) | Unpin CDK version |
| 0.5.0 | 2024-02-20 | [35465](https://github.com/airbytehq/airbyte/pull/35465) | Per-error reporting and continue sync on stream failures |
| 0.4.5 | 2024-02-09 | [35077](https://github.com/airbytehq/airbyte/pull/35077) | Manage dependencies with Poetry. |
| 0.4.4 | 2023-11-29 | [32397](https://github.com/airbytehq/airbyte/pull/32397) | Increase test coverage and migrate to base image |
| 0.4.3 | 2023-09-20 | [30648](https://github.com/airbytehq/airbyte/pull/30648) | Update candidates.json |
| 0.4.2 | 2023-08-02 | [28969](https://github.com/airbytehq/airbyte/pull/28969) | Update CDK version |
| 0.4.1 | 2023-06-28 | [27773](https://github.com/airbytehq/airbyte/pull/27773) | Update following state breaking changes |
| 0.4.0 | 2023-04-26 | [25332](https://github.com/airbytehq/airbyte/pull/25332) | Add new streams: `ActivityFeed`, `Approvals`, `Disciplines`, `Eeoc`, `EmailTemplates`, `Offices`, `ProspectPools`, `Schools`, `Tags`, `UserPermissions`, `UserRoles` |
| 0.3.1 | 2023-03-06 | [23231](https://github.com/airbytehq/airbyte/pull/23231) | Publish using low-code CDK Beta version |
| 0.3.0 | 2022-10-19 | [18154](https://github.com/airbytehq/airbyte/pull/18154) | Extend `Users` stream schema |
| 0.2.11 | 2022-09-27 | [17239](https://github.com/airbytehq/airbyte/pull/17239) | Always install the latest version of Airbyte CDK |
| 0.2.10 | 2022-09-05 | [16338](https://github.com/airbytehq/airbyte/pull/16338) | Implement incremental syncs & fix SATs |
| 0.2.9 | 2022-08-22 | [15800](https://github.com/airbytehq/airbyte/pull/15800) | Bugfix to allow reading sentry.yaml and schemas at runtime |
| 0.2.8 | 2022-08-10 | [15344](https://github.com/airbytehq/airbyte/pull/15344) | Migrate connector to config-based framework |
| 0.2.7 | 2022-04-15 | [11941](https://github.com/airbytehq/airbyte/pull/11941) | Correct Schema data type for Applications, Candidates, Scorecards and Users |
| 0.2.6 | 2021-11-08 | [7607](https://github.com/airbytehq/airbyte/pull/7607) | Implement demographics streams support. Update SAT for demographics streams |
| 0.2.5 | 2021-09-22 | [6377](https://github.com/airbytehq/airbyte/pull/6377) | Refactor the connector to use CDK. Implement additional stream support |
| 0.2.4 | 2021-09-15 | [6238](https://github.com/airbytehq/airbyte/pull/6238) | Add identification of accessible streams for API keys with limited permissions |

</details>
