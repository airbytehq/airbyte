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
| 0.1.3 | 2024-06-06 | [39159](https://github.com/airbytehq/airbyte/pull/39159) | [autopull] Upgrade base image to v1.2.2 |
| 0.1.2 | 2024-05-28 | [38666](https://github.com/airbytehq/airbyte/pull/38666) | Make connector compatible with Builder |
| 0.1.1 | 2024-05-20 | [38421](https://github.com/airbytehq/airbyte/pull/38421) | [autopull] base image + poetry + up_to_date |
| 0.1.0 | 2022-10-22 | [18334](https://github.com/airbytehq/airbyte/pull/18334) | Add Ashby Source Connector |

</details>
