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

The Pivotal Tracker connector should not run into Stripe API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

- Pivotal Tracker API Token

### Setup guide to create the API Token

To obtain an API Token from Pivotal Tracker, follow these steps:

1. Ensure you have a Pivotal Tracker account. If you do not have one yet, you can sign up [here](https://www.pivotaltracker.com/signup/new).
2. Log in to your Pivotal Tracker account.
3. Navigate to your profile page by clicking on your profile picture on the top right and selecting "Profile".
4. Scroll down to the API Tokens section and click on "Create New Token".
5. Give your token a name and select the desired scopes for your token. We recommend selecting "All Scopes".
6. Click on the "Create Token" button.
7. Copy the generated token as it will only be visible once.

### Connector Configuration

To configure the Pivotal Tracker source connector in Airbyte, follow these steps:

1. In your Airbyte dashboard, click on "Create Connection" on the top right.
2. Select "Pivotal Tracker" as the connector you want to create.
3. Enter a name for your connection and paste the API token you obtained earlier in the "api_token" field.
4. Click on the "Test" button to ensure that Airbyte can successfully connect to Pivotal Tracker.
5. Once the test succeeds, click on the "Create" button to save your connection.

You can now create a Pivotal Tracker source sync in Airbyte and start replicating data from Pivotal Tracker. If you encounter any issues with the connector, please refer to the [Pivotal Tracker API documentation](https://www.pivotaltracker.com/help/api/rest/v5) or [create an issue](https://github.com/airbytehq/airbyte/issues) on the Airbyte GitHub repository.