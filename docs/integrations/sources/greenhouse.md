# Greenhouse

This page contains the setup guide and reference information for the Greenhouse source connector. The connector reads recruiting data from the Greenhouse [Harvest API](https://harvestdocs.greenhouse.io/).

## Prerequisites

You need a Greenhouse Harvest API key. To create one:

1. Ask a Greenhouse site administrator to grant your user the **Can manage ALL organization's API Credentials** developer permission, if you don't have it already.
2. In Greenhouse, go to **Configure** > **Dev Center** > **API Credential Management**.
3. Create a **Harvest** API key.
4. Click **Manage Permissions** next to the key, then grant it the `GET` permission for every endpoint you want to sync. Keys created after January 18, 2017 have no endpoint permissions until you grant them.

A Harvest key that can read an endpoint can read everything that endpoint returns. Greenhouse doesn't scope Harvest keys to a subset of jobs, offices, or candidates, so treat the key as full read access to the endpoints you enable.

For details, see the Greenhouse [authentication guide](https://harvestdocs.greenhouse.io/docs/authentication).

## Set up the Greenhouse connector in Airbyte

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account or navigate to the Airbyte Open Source dashboard.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Greenhouse** from the Source type dropdown.
4. Enter the name for the Greenhouse connector.
5. Enter your Harvest **API Key**.
6. Optionally, change **Number of concurrent threads**. The default of 2 helps stay inside Greenhouse's rate limit for one API key. Raise it to 8 only if the key isn't shared with other integrations, and lower it to 1 if you see rate-limit errors.
7. Click **Set up source**.

## Supported sync modes

The Greenhouse source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
- [Incremental - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
- [Incremental - Append + Deduped](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append-deduped)

A stream supports incremental sync only when its Harvest endpoint accepts a date filter. The remaining streams re-read all records on every sync. Most are small lookup resources, but a few, including `activity_feed`, `approvals`, `tags`, and `user_permissions`, fan out one request per parent record and can be slow on large accounts.

## Supported streams

The table lists the Harvest endpoint behind each stream and the cursor field for incremental streams. Endpoints with a `{...}` segment are child streams. The connector reads the parent stream first, then requests the child endpoint once per parent record.

| Stream | Harvest endpoint | Cursor field |
| --- | --- | --- |
| `activity_feed` | `/candidates/{candidate_id}/activity_feed` | — |
| `applications` | `/applications` | `applied_at` |
| `applications_demographics_answers` | `/applications/{application_id}/demographics/answers` | `updated_at` |
| `applications_interviews` | `/applications/{application_id}/scheduled_interviews` | `updated_at` |
| `approvals` | `/jobs/{job_id}/approval_flows` | — |
| `candidates` | `/candidates` | `updated_at` |
| `close_reasons` | `/close_reasons` | — |
| `custom_fields` | `/custom_fields` | — |
| `degrees` | `/degrees` | — |
| `demographics_answer_options` | `/demographics/answer_options` | — |
| `demographics_answers` | `/demographics/answers` | `updated_at` |
| `demographics_answers_answer_options` | `/demographics/questions/{question_id}/answer_options` | — |
| `demographics_question_sets` | `/demographics/question_sets` | — |
| `demographics_question_sets_questions` | `/demographics/question_sets/{question_set_id}/questions` | — |
| `demographics_questions` | `/demographics/questions` | — |
| `departments` | `/departments` | — |
| `disciplines` | `/disciplines` | — |
| `eeoc` | `/eeoc` | `submitted_at` |
| `email_templates` | `/email_templates` | `updated_at` |
| `interviews` | `/scheduled_interviews` | `updated_at` |
| `job_posts` | `/job_posts` | `updated_at` |
| `job_stages` | `/job_stages` | `updated_at` |
| `jobs` | `/jobs` | `updated_at` |
| `jobs_openings` | `/jobs/{job_id}/openings` | — |
| `jobs_stages` | `/jobs/{job_id}/stages` | `updated_at` |
| `offers` | `/offers` | `updated_at` |
| `offices` | `/offices` | — |
| `prospect_pools` | `/prospect_pools` | — |
| `rejection_reasons` | `/rejection_reasons` | — |
| `schools` | `/schools` | — |
| `scorecards` | `/scorecards` | `updated_at` |
| `sources` | `/sources` | — |
| `tags` | `/tags/candidate` | — |
| `user_permissions` | `/users/{user_id}/permissions/jobs` | — |
| `user_roles` | `/user_roles` | — |
| `users` | `/users` | `updated_at` |

For field-level details on each resource, see the [Harvest API reference](https://harvestdocs.greenhouse.io/reference).

## Harvest v1 deprecation

Greenhouse has deprecated Harvest v1 and v2 and plans to remove those endpoints on August 31, 2026. This connector still reads the v1 endpoints listed earlier, and Airbyte is migrating it to Harvest v3. Version 0.8.0 was the first step, changing how the connector builds request URLs and pagination parameters without changing any data it returns.

Greenhouse states that OAuth becomes the only supported authentication method once Greenhouse removes v1 and v2, so expect the connector's credentials to change from a Harvest API key to OAuth client credentials as part of that migration. Watch the changelog on this page for the version that makes the switch, and don't upgrade past it until you have the new credentials ready.

## Performance considerations

Greenhouse rate limits Harvest requests per API key. On v1 and v2, the allowance is the value of the `X-RateLimit-Limit` response header, typically 50, for each 10-second window. The connector retries throttled requests, so a sync recovers on its own. If you see rate-limit failures, lower **Number of concurrent threads**, and remember that other integrations share the limit when they use the same key.

## Troubleshooting

- **A stream syncs zero records but the sync succeeds.** The connector treats an HTTP 403 from Greenhouse as an empty response so that one unauthorized endpoint doesn't fail the whole sync. Check that your Harvest key has the `GET` permission for that stream's endpoint in **API Credential Management**.
- **The connection check fails with an authentication error.** The check reads `/users`. Confirm the key is active and has `GET` permission on the users endpoint.

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version    | Date       | Pull Request                                             | Subject                                                                                                                                                                |
|:-----------|:-----------|:---------------------------------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
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
