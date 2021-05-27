# Asana

## Sync overview

This source can sync data for the [Asana API](https://developers.asana.com/docs). It supports only Full Refresh syncs. 


### Output schema

This Source is capable of syncing the following Streams:

* [Custom fields](https://developers.asana.com/docs/custom-fields)
* [Projects](https://developers.asana.com/docs/projects)
* [Sections](https://developers.asana.com/docs/sections)
* [Stories](https://developers.asana.com/docs/stories)
* [Tags](https://developers.asana.com/docs/tags)
* [Tasks](https://developers.asana.com/docs/tasks)
* [Teams](https://developers.asana.com/docs/teams)
* [Team Memberships](https://developers.asana.com/docs/team-memberships)
* [Users](https://developers.asana.com/docs/users)
* [Workspaces](https://developers.asana.com/docs/workspaces)

### Data type mapping

| Integration Type | Airbyte Type | Notes |
| :--- | :--- | :--- |
| `string` | `string` |  |
| `int`, `float`, `number` | `number` |  |
| `date` | `date` |  |
| `datetime` | `datetime` |  |
| `array` | `array` |  |
| `object` | `object` |  |

### Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental Sync | No |  |
| Namespaces | No |  |

### Performance considerations

The connector is restricted by normal Asana [requests limitation](https://developers.asana.com/docs/rate-limits).

The Asana connector should not run into Asana API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

* Personal Access Token

### Setup guide

Please follow these [steps](https://developers.asana.com/docs/personal-access-token)
to obtain Personal Access Token for your account.

