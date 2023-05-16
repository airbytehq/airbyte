# Pivotal Tracker

## Overview

The Pivotal Tracker source supports Full Refresh syncs. It supports pulling the following streams:

- Activity
- Epics
- Labels
- Project Membership
- Projects
- Releases
- Stories

### Output schema

The output schema for the Pivotal Tracker source includes the following streams:

- [Activity](https://www.pivotaltracker.com/help/api/rest/v5#Activity)
- [Epics](https://www.pivotaltracker.com/help/api/rest/v5#Epics)
- [Labels](https://www.pivotaltracker.com/help/api/rest/v5#Labels)
- [Project Membership](https://www.pivotaltracker.com/help/api/rest/v5#Project_Memberships)
- [Projects](https://www.pivotaltracker.com/help/api/rest/v5#Projects)
- [Releases](https://www.pivotaltracker.com/help/api/rest/v5#Releases)
- [Stories](https://www.pivotaltracker.com/help/api/rest/v5#Stories)

### Features

The Pivotal Tracker connector supports the following features:

| Feature                       | Supported? |
| :---------------------------- | :--------- |
| Full Refresh Sync             | Yes        |
| Incremental - Append Sync     | Coming soon|
| Replicate Incremental Deletes | Coming soon|
| SSL connection                | Yes        |
| Namespaces                    | No         |

### Performance considerations

The Pivotal Tracker connector should not run into Pivotal Tracker API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you encounter any rate limit issues that are not automatically retried successfully.

## Getting started

### Prerequisites

Before you can set up the Pivotal Tracker source, you must have a Pivotal Tracker API token.

### Set up the API Token

To create a Pivotal Tracker API token:

1. Log in to Pivotal Tracker and access your [profile](https://www.pivotaltracker.com/profile).
2. Scroll down to the **Create New Token** section.
3. Click the **Create New Token** button.
4. In the modal that appears, enter a name for the token and click **Create**.
5. Copy the generated token to your clipboard.

### Configure the Connector in Airbyte

To set up the Pivotal Tracker source connector in Airbyte:

1. In Airbyte, navigate to the **Sources** page.
2. Click the **Create New Connection** button.
3. Select the **Pivotal Tracker** source from the list of available sources.
4. Enter a name for the connection and click **Next**.
5. In the **Configuration** tab, enter your Pivotal Tracker API token in the **api_token** field.
6. Click **Test** to verify that Airbyte can connect to Pivotal Tracker using the provided API token.
7. Once the test is successful, click **Next**.
8. In the **Schema** tab, select the streams that you want to sync and enter any additional configuration options.
9. Click **Next**.
10. (Optional) In the **Sync** tab, configure the sync schedule and history preservation settings.
11. Click **Create** to save the connector configuration.

## Changelog

| Version | Date       | Pull Request                                             | Subject         |
| :------ | :--------- | :------------------------------------------------------- | :-------------- |
| 0.1.0   | 2022-04-04 | [11060](https://github.com/airbytehq/airbyte/pull/11060) | Initial Release |