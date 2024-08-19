# Pivotal Tracker

## Overview

The Pivotal Tracker source supports Full Refresh syncs. It supports pulling from :

- Activity
- Epics
- Labels
- Project Membership
- Projects
- Releases
- Stories

### Output schema

Output streams:

- [Activity](https://www.pivotaltracker.com/help/api/rest/v5#Activity)
- [Epics](https://www.pivotaltracker.com/help/api/rest/v5#Epics)
- [Labels](https://www.pivotaltracker.com/help/api/rest/v5#Labels)
- [Project Membership](https://www.pivotaltracker.com/help/api/rest/v5#Project_Memberships)
- [Projects](https://www.pivotaltracker.com/help/api/rest/v5#Projects)
- [Releases](https://www.pivotaltracker.com/help/api/rest/v5#Releases)
- [Stories](https://www.pivotaltracker.com/help/api/rest/v5#Stories)

### Features

| Feature                       | Supported?  |
| :---------------------------- | :---------- |
| Full Refresh Sync             | Yes         |
| Incremental - Append Sync     | Coming soon |
| Replicate Incremental Deletes | Coming soon |
| SSL connection                | Yes         |
| Namespaces                    | No          |

### Performance considerations

The Pivotal Trakcer connector should not run into Stripe API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

- Pivotal Trakcer API Token

### Setup guide to create the API Token

Access your profile [here](https://www.pivotaltracker.com/profile) go down and click in **Create New Token**.
Use this to pull data from Pivotal Tracker.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject         |
| :------ | :--------- | :------------------------------------------------------- | :-------------- |
| 0.3.1   | 2024-08-16 | [44196](https://github.com/airbytehq/airbyte/pull/44196) | Bump source-declarative-manifest version   |
| 0.3.0 | 2024-08-14 | [44087](https://github.com/airbytehq/airbyte/pull/44087) | Refactor connector to manifest-only format |
| 0.2.12 | 2024-08-12 | [43849](https://github.com/airbytehq/airbyte/pull/43849) | Update dependencies |
| 0.2.11 | 2024-08-10 | [43506](https://github.com/airbytehq/airbyte/pull/43506) | Update dependencies |
| 0.2.10 | 2024-08-03 | [43223](https://github.com/airbytehq/airbyte/pull/43223) | Update dependencies |
| 0.2.9 | 2024-07-27 | [42784](https://github.com/airbytehq/airbyte/pull/42784) | Update dependencies |
| 0.2.8 | 2024-07-20 | [42199](https://github.com/airbytehq/airbyte/pull/42199) | Update dependencies |
| 0.2.7 | 2024-07-13 | [41772](https://github.com/airbytehq/airbyte/pull/41772) | Update dependencies |
| 0.2.6 | 2024-07-10 | [41595](https://github.com/airbytehq/airbyte/pull/41595) | Update dependencies |
| 0.2.5 | 2024-07-09 | [41139](https://github.com/airbytehq/airbyte/pull/41139) | Update dependencies |
| 0.2.4 | 2024-07-06 | [40964](https://github.com/airbytehq/airbyte/pull/40964) | Update dependencies |
| 0.2.3 | 2024-06-25 | [40472](https://github.com/airbytehq/airbyte/pull/40472) | Update dependencies |
| 0.2.2 | 2024-06-22 | [40036](https://github.com/airbytehq/airbyte/pull/40036) | Update dependencies |
| 0.2.1 | 2024-06-04 | [39071](https://github.com/airbytehq/airbyte/pull/39071) | [autopull] Upgrade base image to v1.2.1 |
| 0.2.0 | 2024-04-01 | [36499](https://github.com/airbytehq/airbyte/pull/36499) | Migrate to low code |
| 0.1.1 | 2023-10-25 | [11060](https://github.com/airbytehq/airbyte/pull/11060) | Fix schema and check connection |
| 0.1.0 | 2022-04-04 | [11060](https://github.com/airbytehq/airbyte/pull/11060) | Initial Release |


</details>
