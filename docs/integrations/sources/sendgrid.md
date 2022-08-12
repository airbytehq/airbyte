# Sendgrid

## Overview

The Sendgrid source supports Full Refresh syncs. That is, every time a sync is run, Airbyte will copy all rows in the tables and columns you set up for replication into the destination in a new table.

**Note:** SendGrid provides two different kinds of marketing campaigns, "legacy marketing campaigns" and "new marketing campaigns". **Legacy marketing campaigns are not supported by this source connector**. If you are seeing a `403 FORBIDDEN error message for https://api.sendgrid.com/v3/marketing/campaigns`, it might be because your SendGrid account uses legacy marketing campaigns.

### Output schema

Several output streams are available from this source \(campaigns, lists\).

If there are more endpoints you'd like Airbyte to support, please [create an issue.](https://github.com/airbytehq/airbyte/issues/new/choose)

### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental Sync | Coming soon |
| Replicate Incremental Deletes | Coming soon |
| SSL connection | Yes |
| Namespaces | No |

### Performance considerations

The connector is restricted by normal Sendgrid [requests limitation](https://sendgrid.com/docs/API_Reference/Web_API_v3/How_To_Use_The_Web_API_v3/rate_limits.html).

The Sendgrid connector should not run into Sendgrid API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

* Sendgrid Account
* Sendgrid API Key with the following permissions:
    * Read-only access to all resources
    * Full access to marketing resources

### Setup guide

Generate a API key using the [Sendgrid documentation](https://sendgrid.com/docs/ui/account-and-settings/api-keys/#creating-an-api-key).

We recommend creating a key specifically for Airbyte access. This will allow you to control which resources Airbyte should be able to access. The API key should be read-only on all resources except Marketing, where it needs Full Access.

To consume Messages resources requires to purchase an extra on Sendgrid. You can read more about this [here](https://docs.sendgrid.com/api-reference/e-mail-activity)

| Version | Date | Pull Request                                             | Subject                                            |
|:--------| :--- |:---------------------------------------------------------|:---------------------------------------------------|
| 0.2.9   | 2022-06-07 | [15257](https://github.com/airbytehq/airbyte/pull/15257) | Migrate to config-based framework                  |
| 0.2.8   | 2022-06-07 | [13571](https://github.com/airbytehq/airbyte/pull/13571) | Add Message stream                                 |
| 0.2.7   | 2021-09-08 | [5910](https://github.com/airbytehq/airbyte/pull/5910)   | Add Single Sends Stats stream                      |
| 0.2.6   | 2021-07-19 | [4839](https://github.com/airbytehq/airbyte/pull/4839)   | Gracefully handle malformed responses from the API |

