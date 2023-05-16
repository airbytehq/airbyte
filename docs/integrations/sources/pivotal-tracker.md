# Pivotal Tracker

## Overview

The Pivotal Tracker source supports Full Refresh syncs. It supports pulling from:

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

The Pivotal Tracker connector should not run into Stripe API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

- Pivotal Tracker API Token

### Setup guide to create the API Token

1. Go to your [Pivotal Tracker Profile](https://www.pivotaltracker.com/profile).
2. Scroll down and click on **Create New Token**.
3. Name your token.
4. Select the appropriate scopes for your use case.
5. Click on **Create Token**.
6. Copy the newly created token.
7. Return to the Airbyte interface and paste the copied token to the **api_token** field in the **Pivotal Tracker Spec**.

For more information on how to create a Pivotal Tracker API token, please refer to Pivotal Tracker's [official documentation](https://www.pivotaltracker.com/help/articles/api_token/).

## Changelog

| Version | Date       | Pull Request                                             | Subject         |
| :------ | :--------- | :------------------------------------------------------- | :-------------- |
| 0.1.0   | 2022-04-04 | [11060](https://github.com/airbytehq/airbyte/pull/11060) | Initial Release |