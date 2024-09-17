# Pardot

## Overview

The Pardot supports full refresh syncs

### Output schema

Several output streams are available from this source:

- [Campaigns](https://developer.salesforce.com/docs/marketing/pardot/guide/campaigns-v4.html)
- [EmailClicks](https://developer.salesforce.com/docs/marketing/pardot/guide/batch-email-clicks-v4.html)
- [ListMembership](https://developer.salesforce.com/docs/marketing/pardot/guide/list-memberships-v4.html)
- [Lists](https://developer.salesforce.com/docs/marketing/pardot/guide/lists-v4.html)
- [ProspectAccounts](https://developer.salesforce.com/docs/marketing/pardot/guide/prospect-accounts-v4.html)
- [Prospects](https://developer.salesforce.com/docs/marketing/pardot/guide/prospects-v4.html)
- [Users](https://developer.salesforce.com/docs/marketing/pardot/guide/users-v4.html)
- [VisitorActivities](https://developer.salesforce.com/docs/marketing/pardot/guide/visitor-activities-v4.html)
- [Visitors](https://developer.salesforce.com/docs/marketing/pardot/guide/visitors-v4.html)
- [Visits](https://developer.salesforce.com/docs/marketing/pardot/guide/visits-v4.html)

If there are more endpoints you'd like Airbyte to support, please [create an issue.](https://github.com/airbytehq/airbyte/issues/new/choose)

### Features

| Feature           | Supported? |
| :---------------- | :--------- |
| Full Refresh Sync | Yes        |
| Incremental Sync  | No         |
| SSL connection    | No         |
| Namespaces        | No         |

### Performance considerations

The Pardot connector should not run into Pardot API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

- Pardot Account
- Pardot Business Unit ID
- Client ID
- Client Secret
- Refresh Token
- Start Date
- Is Sandbox environment?

### Setup guide

- `pardot_business_unit_id`: Pardot Business ID, can be found at Setup > Pardot > Pardot Account Setup
- `client_id`: The Consumer Key that can be found when viewing your app in Salesforce
- `client_secret`: The Consumer Secret that can be found when viewing your app in Salesforce
- `refresh_token`: Salesforce Refresh Token used for Airbyte to access your Salesforce account. If you don't know what this is, follow [this guide](https://medium.com/@bpmmendis94/obtain-access-refresh-tokens-from-salesforce-rest-api-a324fe4ccd9b) to retrieve it.
- `start_date`: UTC date and time in the format 2017-01-25T00:00:00Z. Any data before this date will not be replicated. Leave blank to skip this filter
- `is_sandbox`: Whether or not the app is in a Salesforce sandbox. If you do not know what this is, assume it is false.
