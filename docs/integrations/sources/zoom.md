# Zoom

## Overview

The following connector allows airbyte users to fetch various meetings & webinar data points from the [Zoom](https://zoom.us) source. This connector is built entirely using the [low-code CDK](https://docs.airbyte.com/connector-development/config-based/low-code-cdk-overview/).

Please note that currently, it only supports Full Refresh syncs. That is, every time a sync is run, Airbyte will copy all rows in the tables and columns you set up for replication into the destination in a new table.

### Output schema

Currently this source supports the following output streams/endpoints from Zoom:

- [Users](https://marketplace.zoom.us/docs/api-reference/zoom-api/users/users)
- [Meetings](https://marketplace.zoom.us/docs/api-reference/zoom-api/meetings/meetings)
  - [Meeting Registrants](https://marketplace.zoom.us/docs/api-reference/zoom-api/meetings/meetingregistrants)
  - [Meeting Polls](https://marketplace.zoom.us/docs/api-reference/zoom-api/meetings/meetingpolls)
  - [Meeting Poll Results](https://marketplace.zoom.us/docs/api-reference/zoom-api/meetings/listpastmeetingpolls)
  - [Meeting Questions](https://marketplace.zoom.us/docs/api-reference/zoom-api/meetings/meetingregistrantsquestionsget)
- [Webinars](https://marketplace.zoom.us/docs/api-reference/zoom-api/webinars/webinars)
  - [Webinar Panelists](https://marketplace.zoom.us/docs/api-reference/zoom-api/webinars/webinarpanelists)
  - [Webinar Registrants](https://marketplace.zoom.us/docs/api-reference/zoom-api/webinars/webinarregistrants)
  - [Webinar Absentees](https://marketplace.zoom.us/docs/api-reference/zoom-api/webinars/webinarabsentees)
  - [Webinar Polls](https://marketplace.zoom.us/docs/api-reference/zoom-api/webinars/webinarpolls)
  - [Webinar Poll Results](https://marketplace.zoom.us/docs/api-reference/zoom-api/webinars/listpastwebinarpollresults)
  - [Webinar Questions](https://marketplace.zoom.us/docs/api-reference/zoom-api/webinars/webinarregistrantsquestionsget)
  - [Webinar Tracking Sources](https://marketplace.zoom.us/docs/api-reference/zoom-api/webinars/gettrackingsources)
  - [Webinar Q&A Results](https://marketplace.zoom.us/docs/api-reference/zoom-api/webinars/listpastwebinarqa)
- [Report Meetings](https://marketplace.zoom.us/docs/api-reference/zoom-api/reports/reportmeetingdetails)
- [Report Meeting Participants](https://marketplace.zoom.us/docs/api-reference/zoom-api/reports/reportmeetingparticipants)
- [Report Webinars](https://marketplace.zoom.us/docs/api-reference/zoom-api/reports/reportwebinardetails)
- [Report Webinar Participants](https://marketplace.zoom.us/docs/api-reference/zoom-api/reports/reportwebinarparticipants)

If there are more endpoints you'd like Airbyte to support, please [create an issue.](https://github.com/airbytehq/airbyte/issues/new/choose)

### Features

| Feature                       | Supported?  |
| :---------------------------- | :---------- |
| Full Refresh Sync             | Yes         |
| Incremental Sync              | Coming soon |
| Replicate Incremental Deletes | Coming soon |
| SSL connection                | Yes         |
| Namespaces                    | No          |

### Performance considerations

Most of the endpoints this connector access is restricted by standard Zoom [requests limitation](https://marketplace.zoom.us/docs/api-reference/rate-limits#rate-limit-changes), with a few exceptions. For more info, please check zoom API documentation. We’ve added appropriate retries if we hit the rate-limiting threshold.

Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

- Zoom Server-to-Server Oauth App

### Setup guide

Please read [How to generate your Server-to-Server OAuth app ](https://developers.zoom.us/docs/internal-apps/s2s-oauth/).

:::info

JWT Tokens are deprecated, only Server-to-Server works now. [link to Zoom](https://developers.zoom.us/docs/internal-apps/jwt-faq/)

:::

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                              |
| :------ | :--------- | :------------------------------------------------------- | :--------------------------------------------------- |
| 1.1.14 | 2024-08-31 | [45037](https://github.com/airbytehq/airbyte/pull/45037) | Update dependencies |
| 1.1.13 | 2024-08-24 | [44676](https://github.com/airbytehq/airbyte/pull/44676) | Update dependencies |
| 1.1.12 | 2024-08-17 | [44249](https://github.com/airbytehq/airbyte/pull/44249) | Update dependencies |
| 1.1.11 | 2024-08-10 | [43578](https://github.com/airbytehq/airbyte/pull/43578) | Update dependencies |
| 1.1.10 | 2024-08-03 | [43149](https://github.com/airbytehq/airbyte/pull/43149) | Update dependencies |
| 1.1.9 | 2024-07-27 | [42652](https://github.com/airbytehq/airbyte/pull/42652) | Update dependencies |
| 1.1.8 | 2024-07-20 | [42212](https://github.com/airbytehq/airbyte/pull/42212) | Update dependencies |
| 1.1.7 | 2024-07-13 | [41813](https://github.com/airbytehq/airbyte/pull/41813) | Update dependencies |
| 1.1.6 | 2024-07-10 | [41486](https://github.com/airbytehq/airbyte/pull/41486) | Update dependencies |
| 1.1.5 | 2024-07-09 | [41316](https://github.com/airbytehq/airbyte/pull/41316) | Update dependencies |
| 1.1.4 | 2024-07-06 | [40986](https://github.com/airbytehq/airbyte/pull/40986) | Update dependencies |
| 1.1.3 | 2024-06-26 | [40509](https://github.com/airbytehq/airbyte/pull/40509) | Update dependencies |
| 1.1.2 | 2024-06-22 | [40141](https://github.com/airbytehq/airbyte/pull/40141) | Update dependencies |
| 1.1.1 | 2024-06-06 | [39279](https://github.com/airbytehq/airbyte/pull/39279) | [autopull] Upgrade base image to v1.2.2 |
| 1.1.0 | 2024-02-22 | [35369](https://github.com/airbytehq/airbyte/pull/35369) | Publish S2S Oauth connector with fixed authenticator |
| 1.0.0   | 2023-7-28  | [25308](https://github.com/airbytehq/airbyte/pull/25308) | Replace JWT Auth methods with server-to-server Oauth |
| 0.1.1   | 2022-11-30 | [19939](https://github.com/airbytehq/airbyte/pull/19939) | Upgrade CDK version to fix bugs with SubStreamSlicer |
| 0.1.0   | 2022-10-25 | [18179](https://github.com/airbytehq/airbyte/pull/18179) | Initial Release                                      |

</details>
