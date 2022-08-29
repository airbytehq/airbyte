# Sendgrid

This page contains the setup guide and reference information for the Sendgrid source connector.

## Prerequisites

**Note:** Sendgrid provides two different kinds of marketing campaigns, "legacy marketing campaigns" and "new marketing campaigns". **Legacy marketing campaigns are not supported by this source connector**. 
If you are seeing a `403 FORBIDDEN error message for https://api.sendgrid.com/v3/marketing/campaigns`, it might be because your SendGrid account uses legacy marketing campaigns.

Generate an API key using the [Sendgrid documentation](https://sendgrid.com/docs/ui/account-and-settings/api-keys/#creating-an-api-key).

We recommend creating a key specifically for Airbyte access. This will allow you to control which resources Airbyte should be able to access. The API key should be read-only on all resources except Marketing, where it needs Full Access.

To consume Messages resources requires to purchase an extra on Sendgrid. You can read more about this [here](https://docs.sendgrid.com/api-reference/e-mail-activity)

## Setup guide
### Step 1: Set up Sendgrid

* Sendgrid Account
* Sendgrid API Key with the following permissions:
    * Read-only access to all resources
    * Full access to marketing resources

## Step 2: Set up the Sendgrid connector in Airbyte

### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.io/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+new source**.
3. On the Set up the source page, enter the name for the Sendgrid connector and select **Sendgrid** from the Source type dropdown.
4. Enter your `apikey`.
5. Enter your `start_time`. 
6. Click **Set up source**.

### For Airbyte OSS:

1. Navigate to the Airbyte Open Source dashboard.
2. Set the name for your source. 
3. Enter your `apikey`.
4. Enter your `start_time`. 
5. Click **Set up source**.

## Supported sync modes

The Sendgrid source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature                       | Supported?  |
| :---------------------------- | :---------- |
| Full Refresh Sync             | Yes         |
| Incremental Sync              | Coming soon |
| Replicate Incremental Deletes | Coming soon |
| SSL connection                | Yes         |
| Namespaces                    | No          |

## Supported Streams

* Campaigns 
* Lists 
* Contacts 
* Stats automations 
* Segments 
* Single_sends 
* Templates 
* Global suppression 
* Suppression groups 
* Suppression group members 
* Blocks 
* Bounces 
* Invalid emails 
* Spam reports 
* Messages

## Performance considerations

The connector is restricted by normal Sendgrid [requests limitation](https://sendgrid.com/docs/API_Reference/Web_API_v3/How_To_Use_The_Web_API_v3/rate_limits.html).

## Changelog

| Version | Date       | Pull Request                                             | Subject                                            |
|:--------| :--------- |:---------------------------------------------------------|:---------------------------------------------------|
| 0.2.12  | 2022-08-24 | [15911](https://github.com/airbytehq/airbyte/pull/15911) | Bugfix to allowing reading schemas at runtime      |
| 0.2.11  | 2022-08-19 | [15800](https://github.com/airbytehq/airbyte/pull/15800) | Bugfix to allow reading sentry.yaml at runtime     |
| 0.2.10  | 2022-08-17 | [15734](https://github.com/airbytehq/airbyte/pull/15734) | Fix yaml based on the new schema validator         |
| 0.2.9   | 2022-08-11 | [15257](https://github.com/airbytehq/airbyte/pull/15257) | Migrate to config-based framework                  |
| 0.2.8   | 2022-06-07 | [13571](https://github.com/airbytehq/airbyte/pull/13571) | Add Message stream                                 |
| 0.2.7   | 2021-09-08 | [5910](https://github.com/airbytehq/airbyte/pull/5910)   | Add Single Sends Stats stream                      |
| 0.2.6   | 2021-07-19 | [4839](https://github.com/airbytehq/airbyte/pull/4839)   | Gracefully handle malformed responses from the API |
