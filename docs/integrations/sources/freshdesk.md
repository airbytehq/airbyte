# Freshdesk

## Overview

The Freshdesk source supports Full Refresh syncs. That is, every time a sync is run, Airbyte will copy all rows in the tables and columns you set up for replication into the destination in a new table.

### Output schema

Several output streams are available from this source:

* [Agents](https://developers.freshdesk.com/api/#agents)
* [Companies](https://developers.freshdesk.com/api/#companies)
* [Contacts](https://developers.freshdesk.com/api/#contacts)
* [Groups](https://developers.freshdesk.com/api/#groups)
* [Roles](https://developers.freshdesk.com/api/#roles)
* [Skills](https://developers.freshdesk.com/api/#skills)
* [Surveys](https://developers.freshdesk.com/api/#surveys)
* [Tickets](https://developers.freshdesk.com/api/#tickets)
* [Time Entries](https://developers.freshdesk.com/api/#time-entries)

If there are more endpoints you'd like Airbyte to support, please [create an issue.](https://github.com/airbytehq/airbyte/issues/new/choose)

### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental Sync | Coming soon |
| Replicate Incremental Deletes | Coming soon |
| SSL connection | Yes |

### Performance considerations

The Freshdesk connector should not run into Freshdesk API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

* Freshdesk Account
* Freshdesk API Key

### Setup guide

Please read [How to find your API key](https://support.freshdesk.com/support/solutions/articles/215517).

