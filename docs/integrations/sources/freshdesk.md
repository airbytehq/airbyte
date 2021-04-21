# Freshdesk

## Overview

The Freshdesk supports full refresh and incremental sync. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run. There are two types of incremental sync:

* server level \(native\) - when API supports filter on specific columns that Airbyte use to track changes \(`updated_at`, `created_at`, etc\)
* client level - when API doesn't support filter and Airbyte performs filtration on its side.

### Output schema

Several output streams are available from this source:

* [Agents](https://developers.freshdesk.com/api/#agents)
* [Companies](https://developers.freshdesk.com/api/#companies)
* [Contacts](https://developers.freshdesk.com/api/#contacts) \(Native Incremental Sync\)
* [Conversations](https://developers.freshdesk.com/api/#conversations)
* [Groups](https://developers.freshdesk.com/api/#groups)
* [Roles](https://developers.freshdesk.com/api/#roles)
* [Satisfaction Ratings](https://developers.freshdesk.com/api/#satisfaction-ratings)
* [Skills](https://developers.freshdesk.com/api/#skills)
* [Surveys](https://developers.freshdesk.com/api/#surveys)
* [Tickets](https://developers.freshdesk.com/api/#tickets) \(Native Incremental Sync\)
* [Time Entries](https://developers.freshdesk.com/api/#time-entries)

If there are more endpoints you'd like Airbyte to support, please [create an issue.](https://github.com/airbytehq/airbyte/issues/new/choose)

### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental Sync | Yes |
| SSL connection | Yes |
| Namespaces | No |

### Performance considerations

The Freshdesk connector should not run into Freshdesk API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

* Freshdesk Account
* Freshdesk API Key

### Setup guide

Please read [How to find your API key](https://support.freshdesk.com/support/solutions/articles/215517).

