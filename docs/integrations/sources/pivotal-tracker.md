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
| 0.2.0   | 2024-04-01 | [36499](https://github.com/airbytehq/airbyte/pull/36499) | Migrate to low code |
| 0.1.1   | 2023-10-25 | [11060](https://github.com/airbytehq/airbyte/pull/11060) | Fix schema and check connection |
| 0.1.0   | 2022-04-04 | [11060](https://github.com/airbytehq/airbyte/pull/11060) | Initial Release                 |

</details>