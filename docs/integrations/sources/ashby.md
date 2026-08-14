# Ashby

<HideInUI>

This page contains the setup guide and reference information for the [Ashby](https://www.ashbyhq.com/) source connector.

</HideInUI>

## Prerequisites

- An Ashby account
- An Ashby API key with the appropriate permissions for the streams you want to sync. See the [Ashby authentication docs](https://developers.ashbyhq.com/reference/authentication) for details on how to create an API key.

Your API key must have read permissions enabled for the modules that correspond to the streams you want to sync:

| Ashby permission module | Streams |
| :--- | :--- |
| Candidates | `applications`, `application_criteria_evaluations`, `candidates` |
| Interviews | `interviews`, `interview_stages`, `interview_schedules` |
| Jobs | `jobs`, `job_postings` |
| Hiring Process | `archive_reasons`, `candidate_tags`, `custom_fields`, `feedback_form_definitions`, `sources` |
| Organization *(always required)* | `departments`, `locations`, `users` — The connection check validates connectivity using the `users` stream, so you must enable this permission even if you only intend to sync streams from other modules. Without it, the check fails with a `403 missing_endpoint_permission` error. |
| Offers | `offers` |

:::note
The `application_criteria_evaluations` stream requires the AI Application Review feature to be enabled for your Ashby organization. If this feature is not enabled, the stream returns empty results.
:::

## Setup guide

1. Log in to your Ashby account.
2. Generate an API key following the [Ashby authentication guide](https://developers.ashbyhq.com/reference/authentication). Grant the API key read permissions for the modules listed in the prerequisites. At minimum, you must enable the **Organization** read permission (required for the connection check) plus read permissions for any additional modules whose streams you want to sync.
3. In Airbyte, create a new Ashby source.
4. Enter your **API key**.
5. Enter a **Start date** in `YYYY-MM-DDTHH:MM:SSZ` format. The connector sends this date as the `createdAfter` filter on the `applications` and `interview_schedules` streams, so records created before it aren't replicated. The date also limits `application_criteria_evaluations`, because that stream reads the same filtered application list to decide which applications to request evaluations for. All other streams ignore the start date and always return everything the API exposes.

## Supported sync modes

| Feature | Supported |
| :--- | :--- |
| Full Refresh | Yes |
| Incremental - Append | No |

Every sync re-reads each selected stream in full, subject to the start date where it applies. Many Ashby `.list` endpoints support incremental sync through a `syncToken`, but this connector doesn't use it.

## Supported streams

This source syncs the following streams:

- [applications](https://developers.ashbyhq.com/reference/applicationlist)
- [application_criteria_evaluations](https://developers.ashbyhq.com/reference/applicationlistcriteriaevaluations) (substream of applications)
- [archive_reasons](https://developers.ashbyhq.com/reference/archivereasonlist)
- [candidate_tags](https://developers.ashbyhq.com/reference/candidatetaglist)
- [candidates](https://developers.ashbyhq.com/reference/candidatelist)
- [custom_fields](https://developers.ashbyhq.com/reference/customfieldlist)
- [departments](https://developers.ashbyhq.com/reference/departmentlist)
- [feedback_form_definitions](https://developers.ashbyhq.com/reference/feedbackformdefinitionlist)
- [interview_schedules](https://developers.ashbyhq.com/reference/interviewschedulelist)
- [interviews](https://developers.ashbyhq.com/reference/interviewlist)
- [interview_stages](https://developers.ashbyhq.com/reference/interviewstagelist)
- [job_postings](https://developers.ashbyhq.com/reference/jobpostinglist)
- [jobs](https://developers.ashbyhq.com/reference/joblist)
- [locations](https://developers.ashbyhq.com/reference/locationlist)
- [offers](https://developers.ashbyhq.com/reference/offerlist)
- [sources](https://developers.ashbyhq.com/reference/sourcelist)
- [users](https://developers.ashbyhq.com/reference/userlist)

The `application_criteria_evaluations` stream is a substream of `applications`. The connector requests evaluations only for applications whose current interview stage has the type `PreInterviewScreen` and whose status is neither `Archived` nor `Hired`, so it doesn't cover every application in your account. Each record carries an `application_id` field copied from the parent application, which is how you join evaluations back to `applications`. This stream has no primary key, and the connector doesn't paginate the evaluations endpoint, so only the first page of evaluations is synced for each application.

## Performance considerations

Ashby doesn't publish a rate limit for the `.list` endpoints this connector reads, and the connector reads one stream at a time, so syncs are unlikely to be throttled. Ashby's rate limits apply per organization, so an API key shared with other integrations has less headroom.

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                     |
|:--------| :--------- | :------------------------------------------------------- |:--------------------------------------------|
| 0.3.9 | 2026-08-14 | [PRNUMBER](https://github.com/airbytehq/airbyte/pull/PRNUMBER) | Send the pagination page size as the documented `limit` field so streams request 100 records per page and make fewer API calls |
| 0.3.8 | 2026-08-11 | [84215](https://github.com/airbytehq/airbyte/pull/84215) | Promoted release candidate to GA |
| 0.3.8-rc.5 | 2026-08-11 | [84214](https://github.com/airbytehq/airbyte/pull/84214) | Revert the concurrency work from 0.3.8-rc.1 through 0.3.8-rc.3: remove the API budget, concurrency level, and `num_workers` option. |
| 0.3.8-rc.4 | 2026-08-11 | [83816](https://github.com/airbytehq/airbyte/pull/83816) | Add missing application, candidate, and source fields to the declared schemas, and remove duplicated unreferenced manifest blocks. |
| 0.3.8-rc.3 | 2026-05-26 | [78434](https://github.com/airbytehq/airbyte/pull/78434) | Decrease default concurrency to 2 and add explicit worker count plus API request budget for the next rollout. |
| 0.3.8-rc.2 | 2026-05-21 | [78307](https://github.com/airbytehq/airbyte/pull/78307) | Decrease default concurrency to 3 after Phase 1 rollout monitoring found source-read regressions and a 429 retry warning. |
| 0.3.8-rc.1 | 2026-05-18 | [77048](https://github.com/airbytehq/airbyte/pull/77048) | Add concurrency support with default_concurrency=4 for concurrent stream reads |
| 0.3.7 | 2026-04-28 | [77144](https://github.com/airbytehq/airbyte/pull/77144) | Update dependencies |
| 0.3.6 | 2026-04-21 | [76510](https://github.com/airbytehq/airbyte/pull/76510) | Update dependencies |
| 0.3.5 | 2026-03-31 | [75881](https://github.com/airbytehq/airbyte/pull/75881) | Update dependencies |
| 0.3.4 | 2026-03-24 | [75325](https://github.com/airbytehq/airbyte/pull/75325) | Update dependencies |
| 0.3.3 | 2026-03-10 | [74490](https://github.com/airbytehq/airbyte/pull/74490) | Update dependencies |
| 0.3.2 | 2026-02-24 | [73805](https://github.com/airbytehq/airbyte/pull/73805) | Update dependencies |
| 0.3.1 | 2026-02-17 | [60692](https://github.com/airbytehq/airbyte/pull/60692) | Update dependencies |
| 0.3.0 | 2026-02-13 | [73244](https://github.com/airbytehq/airbyte/pull/73244) | Add interviews, interview_stages, and application_criteria_evaluations streams |
| 0.2.23 | 2025-05-10 | [59853](https://github.com/airbytehq/airbyte/pull/59853) | Update dependencies |
| 0.2.22 | 2025-05-03 | [59322](https://github.com/airbytehq/airbyte/pull/59322) | Update dependencies |
| 0.2.21 | 2025-04-26 | [58746](https://github.com/airbytehq/airbyte/pull/58746) | Update dependencies |
| 0.2.20 | 2025-04-19 | [58271](https://github.com/airbytehq/airbyte/pull/58271) | Update dependencies |
| 0.2.19 | 2025-04-12 | [57150](https://github.com/airbytehq/airbyte/pull/57150) | Update dependencies |
| 0.2.18 | 2025-03-29 | [56594](https://github.com/airbytehq/airbyte/pull/56594) | Update dependencies |
| 0.2.17 | 2025-03-22 | [56140](https://github.com/airbytehq/airbyte/pull/56140) | Update dependencies |
| 0.2.16 | 2025-03-08 | [55387](https://github.com/airbytehq/airbyte/pull/55387) | Update dependencies |
| 0.2.15 | 2025-03-01 | [54888](https://github.com/airbytehq/airbyte/pull/54888) | Update dependencies |
| 0.2.14 | 2025-02-22 | [54234](https://github.com/airbytehq/airbyte/pull/54234) | Update dependencies |
| 0.2.13 | 2025-02-15 | [53874](https://github.com/airbytehq/airbyte/pull/53874) | Update dependencies |
| 0.2.12 | 2025-02-08 | [53407](https://github.com/airbytehq/airbyte/pull/53407) | Update dependencies |
| 0.2.11 | 2025-02-01 | [52893](https://github.com/airbytehq/airbyte/pull/52893) | Update dependencies |
| 0.2.10 | 2025-01-25 | [52162](https://github.com/airbytehq/airbyte/pull/52162) | Update dependencies |
| 0.2.9 | 2025-01-18 | [51710](https://github.com/airbytehq/airbyte/pull/51710) | Update dependencies |
| 0.2.8 | 2025-01-11 | [51292](https://github.com/airbytehq/airbyte/pull/51292) | Update dependencies |
| 0.2.7 | 2024-12-28 | [50493](https://github.com/airbytehq/airbyte/pull/50493) | Update dependencies |
| 0.2.6 | 2024-12-21 | [50207](https://github.com/airbytehq/airbyte/pull/50207) | Update dependencies |
| 0.2.5 | 2024-12-14 | [49572](https://github.com/airbytehq/airbyte/pull/49572) | Update dependencies |
| 0.2.4 | 2024-12-12 | [49014](https://github.com/airbytehq/airbyte/pull/49014) | Update dependencies |
| 0.2.3 | 2024-11-04 | [48196](https://github.com/airbytehq/airbyte/pull/48196) | Update dependencies |
| 0.2.2 | 2024-10-29 | [47729](https://github.com/airbytehq/airbyte/pull/47729) | Update dependencies |
| 0.2.1 | 2024-10-28 | [47616](https://github.com/airbytehq/airbyte/pull/47616) | Update dependencies |
| 0.2.0 | 2024-08-19 | [44420](https://github.com/airbytehq/airbyte/pull/44420) | Refactor connector to manifest-only format |
| 0.1.16 | 2024-08-17 | [44288](https://github.com/airbytehq/airbyte/pull/44288) | Update dependencies |
| 0.1.15 | 2024-08-12 | [43780](https://github.com/airbytehq/airbyte/pull/43780) | Update dependencies |
| 0.1.14 | 2024-08-10 | [43491](https://github.com/airbytehq/airbyte/pull/43491) | Update dependencies |
| 0.1.13 | 2024-08-03 | [43080](https://github.com/airbytehq/airbyte/pull/43080) | Update dependencies |
| 0.1.12 | 2024-07-27 | [42658](https://github.com/airbytehq/airbyte/pull/42658) | Update dependencies |
| 0.1.11 | 2024-07-20 | [42220](https://github.com/airbytehq/airbyte/pull/42220) | Update dependencies |
| 0.1.10 | 2024-07-17 | [42028](https://github.com/airbytehq/airbyte/pull/42028) | Fix typo in application stream |
| 0.1.9 | 2024-07-13 | [41818](https://github.com/airbytehq/airbyte/pull/41818) | Update dependencies |
| 0.1.8 | 2024-07-10 | [41379](https://github.com/airbytehq/airbyte/pull/41379) | Update dependencies |
| 0.1.7 | 2024-07-09 | [41271](https://github.com/airbytehq/airbyte/pull/41271) | Update dependencies |
| 0.1.6 | 2024-07-06 | [40971](https://github.com/airbytehq/airbyte/pull/40971) | Update dependencies |
| 0.1.5 | 2024-06-25 | [40469](https://github.com/airbytehq/airbyte/pull/40469) | Update dependencies |
| 0.1.4 | 2024-06-22 | [40107](https://github.com/airbytehq/airbyte/pull/40107) | Update dependencies |
| 0.1.3 | 2024-06-06 | [39159](https://github.com/airbytehq/airbyte/pull/39159) | [autopull] Upgrade base image to v1.2.2 |
| 0.1.2 | 2024-05-28 | [38666](https://github.com/airbytehq/airbyte/pull/38666) | Make connector compatible with Builder |
| 0.1.1 | 2024-05-20 | [38421](https://github.com/airbytehq/airbyte/pull/38421) | [autopull] base image + poetry + up_to_date |
| 0.1.0 | 2022-10-22 | [18334](https://github.com/airbytehq/airbyte/pull/18334) | Add Ashby Source Connector |

</details>
