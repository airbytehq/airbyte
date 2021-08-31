# Pipedrive

## Overview

The Pipedrive connector can be used to sync your Pipedrive data. It supports full refresh sync for Deals, Leads, Activities, ActivityFields, 
Persons, Pipelines, Stages, Users streams and incremental sync for Activities, Deals, Persons, Pipelines, Stages, Users streams.

There was a priority to include at least a single stream of each stream type which is present on Pipedrive, so the list of the supported 
streams is meant to be easily extendable. By the way, we can only support incremental stream support for the streams listed 
[there](https://developers.pipedrive.com/docs/api/v1/Recents#getRecents). 

### Output schema

Several output streams are available from this source:

* [Activities](https://developers.pipedrive.com/docs/api/v1/Activities#getActivities), 
  retrieved by [getRecents](https://developers.pipedrive.com/docs/api/v1/Recents#getRecents) (incremental)
* [ActivityFields](https://developers.pipedrive.com/docs/api/v1/ActivityFields#getActivityFields)
* [Deals](https://developers.pipedrive.com/docs/api/v1/Deals#getDeals),
  retrieved by [getRecents](https://developers.pipedrive.com/docs/api/v1/Recents#getRecents) (incremental)
* [Leads](https://developers.pipedrive.com/docs/api/v1/Leads#getLeads)
* [Persons](https://developers.pipedrive.com/docs/api/v1/Persons#getPersons),
  retrieved by [getRecents](https://developers.pipedrive.com/docs/api/v1/Recents#getRecents) (incremental)
* [Pipelines](https://developers.pipedrive.com/docs/api/v1/Pipelines#getPipelines),
  retrieved by [getRecents](https://developers.pipedrive.com/docs/api/v1/Recents#getRecents) (incremental)
* [Stages](https://developers.pipedrive.com/docs/api/v1/Stages#getStages),
  retrieved by [getRecents](https://developers.pipedrive.com/docs/api/v1/Recents#getRecents) (incremental)
* [Users](https://developers.pipedrive.com/docs/api/v1/Users#getUsers),
  retrieved by [getRecents](https://developers.pipedrive.com/docs/api/v1/Recents#getRecents) (incremental)

### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental Sync | Yes |
| Replicate Incremental Deletes | No |
| SSL connection | Yes |
| Namespaces | No |

### Performance considerations

The Pipedrive connector will gracefully handle rate limits. For more information, see [the Pipedrive docs for rate limitations](https://pipedrive.readme.io/docs/core-api-concepts-rate-limiting).

## Getting started

### Requirements

* Pipedrive Account with wright to generate API Token

### Setup guide

This connector supports only authentication with API Token. To obtain API Token follow the instructions below:

#### Enable API:
1. Click Manage users from the left-side menu.
1. Click on the Permission sets tab.
1. Choose the set where the user (who needs the API enabled) belongs to.
1. Lastly, click on "use API" on the right-hand side section (you need to scroll down a bit). 
   Now all users who belong in the set that has the API enabled can find their API token under 
   Settings > Personal Preferences > API in their Pipedrive web app.
   
See [Enabling API for company users](https://pipedrive.readme.io/docs/enabling-api-for-company-users) for more info.
   
#### How to find the API token:
1. Account name (on the top right)
1. Company settings
1. Personal preferences
1. API
1. Copy API Token

See [How to find the API token](https://pipedrive.readme.io/docs/how-to-find-the-api-token) for more info.


## Changelog

| Version | Date       | Pull Request | Subject |
| :------ | :--------  | :-----       | :------ |
| 0.1.3   | 2021-08-26 | [5642](https://github.com/airbytehq/airbyte/pull/5642) | Remove date-time from deals stream  |
| 0.1.2   | 2021-07-23 | [4912](https://github.com/airbytehq/airbyte/pull/4912) | Update money type to support floating point  |
| 0.1.1   | 2021-07-19 | [4686](https://github.com/airbytehq/airbyte/pull/4686) | Update spec.json |
| 0.1.0   | 2021-07-19 | [4686](https://github.com/airbytehq/airbyte/pull/4686) | Release Pipedrive connector! |