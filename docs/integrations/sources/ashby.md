# Ashby

## Sync overview

The Ashby source supports both Full Refresh only.

This source can sync data for the [Ashby API](https://developers.ashbyhq.com/reference).

### Output schema

This Source is capable of syncing the following core Streams:

- [applications](https://developers.ashbyhq.com/reference/applicationlist)
- [archive_reasons](https://developers.ashbyhq.com/reference/archivereasonlist)
- [candidate_tags](https://developers.ashbyhq.com/reference/candidatetaglist)
- [candidates](https://developers.ashbyhq.com/reference/candidatelist)
- [custom_fields](https://developers.ashbyhq.com/reference/customfieldlist)
- [departments](https://developers.ashbyhq.com/reference/departmentlist)
- [feedback_form_definitions](https://developers.ashbyhq.com/reference/feedbackformdefinitionlist)
- [interview_schedules](https://developers.ashbyhq.com/reference/interviewschedulelist)
- [job_postings](https://developers.ashbyhq.com/reference/jobpostinglist)
- [jobs](https://developers.ashbyhq.com/reference/joblist)
- [locations](https://developers.ashbyhq.com/reference/locationlist)
- [offers](https://developers.ashbyhq.com/reference/offerlist)
- [sources](https://developers.ashbyhq.com/reference/sourcelist)
- [users](https://developers.ashbyhq.com/reference/userlist)

### Features

| Feature                   | Supported?\(Yes/No\) | Notes |
| :------------------------ | :------------------- | :---- |
| Full Refresh Sync         | Yes                  |       |
| Incremental - Append Sync | No                   |       |
| Namespaces                | No                   |       |

### Performance considerations

The Ashby connector should not run into Ashby API limitations under normal usage.

## Requirements

- **Ashby API key**. See the [Ashby docs](https://developers.ashbyhq.com/reference/authentication) for information on how to obtain an API key.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                     |
|:--------| :--------- | :------------------------------------------------------- |:--------------------------------------------|
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
