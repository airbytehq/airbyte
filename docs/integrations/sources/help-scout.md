# Wikipedia Pageviews

This page contains the setup guide and reference information for the Help Scout source connector.

## Prerequisites

1. Create a Help Scout account.
2. Create an application and note the App ID and App Secret.
3. Navigate to `https://secure.helpscout.net/authentication/authorizeClientApplication?client_id={application_id}&state={your_secret}`
4. Copy the `code` param from the redirection URL
5. Then make a post request with the 3 params you need as seen here: ```
curl -X POST https://api.helpscout.net/v2/oauth2/token \
 --data 'code={code}' \
 --data 'client_id={application_id}' \
 --data 'client_secret={application_secret}' \
 --data 'grant_type=authorization_code'
```


## Setup guide

## Step 1: Set up the Help Scout connector in Airbyte

### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.io/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+new source**.
3. On the Set up the source page, enter the name for the Help Scout connector and select **Help Scout** from the Source type dropdown.
4. Enter your parameters.
5. Click **Set up source**.

### For Airbyte OSS:

1. Navigate to the Airbyte Open Source dashboard.
2. Set the name for your source.
3. Enter your parameters.
4. Click **Set up source**.

## Supported sync modes

The Help Scout source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature                       | Supported? |
| :---------------------------- | :--------- |
| Full Refresh Sync             | Yes        |
| Incremental Sync              | No         |
| Replicate Incremental Deletes | No         |
| SSL connection                | Yes        |
| Namespaces                    | No         |

## Supported Streams

- Conversations
- Conversation threads
- Customers
- Mailboxes
- Mailbox Fields
- Mailbox Folders
- Users
- Workflows

## Performance considerations

Unknown

## Changelog

| Version | Date       | Pull Request                                           | Subject        |
| :------ | :--------- | :----------------------------------------------------- | :------------- |
| 0.1.0   | 2023-02-25 | [#21489](https://github.com/airbytehq/airbyte/pull/21489) | Initial commit |
