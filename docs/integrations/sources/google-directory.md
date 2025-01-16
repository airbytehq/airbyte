# Google Directory

## Overview

The Directory source supports Full Refresh syncs. It uses [Google Directory API](https://developers.google.com/admin-sdk/directory/v1/get-start/getting-started).

### Output schema

This Source is capable of syncing the following Streams:

- [users](https://developers.google.com/admin-sdk/directory/v1/guides/manage-users#get_all_users)
- [groups](https://developers.google.com/admin-sdk/directory/v1/guides/manage-groups#get_all_domain_groups)
- [group members](https://developers.google.com/admin-sdk/directory/v1/guides/manage-group-members#get_all_members)

### Data type mapping

| Integration Type | Airbyte Type | Notes |
| :--------------- | :----------- | :---- |
| `string`         | `string`     |       |
| `number`         | `number`     |       |
| `array`          | `array`      |       |
| `object`         | `object`     |       |

### Features

| Feature                       | Supported?\(Yes/No\) | Notes |
| :---------------------------- | :------------------- | :---- |
| Full Refresh Sync             | Yes                  |       |
| Incremental Sync              | No                   |       |
| Replicate Incremental Deletes | Coming soon          |       |
| SSL connection                | Yes                  |       |
| Namespaces                    | No                   |       |

### Performance considerations

This connector attempts to back off gracefully when it hits Directory API's rate limits. To find more information about limits, see [Google Directory's Limits and Quotas](https://developers.google.com/admin-sdk/directory/v1/limits) documentation.

## Getting Started \(Airbyte Cloud\)

1. Click `OAuth2.0 authorization` then `Authenticate your Google Directory account`.
2. You're done.

## Getting Started \(Airbyte Open Source\)

Google APIs use the OAuth 2.0 protocol for authentication and authorization. This connector supports [Web server application](https://developers.google.com/identity/protocols/oauth2#webserver) and [Service accounts](https://developers.google.com/identity/protocols/oauth2#serviceaccount) scenarios. Therefore, there are 2 options of setting up authorization for this source:

- Use your Google account and authorize over Google's OAuth on connection setup. Select "Default OAuth2.0 authorization" from dropdown list.
- Create service account specifically for Airbyte.

### Service account requirements

- Credentials to a Google Service Account with delegated Domain Wide Authority
- Email address of the workspace admin which created the Service Account

### Create a Service Account with delegated domain wide authority

Follow the Google Documentation for performing [Domain Wide Delegation of Authority](https://developers.google.com/admin-sdk/directory/v1/guides/delegation) to create a Service account with delegated domain wide authority. This account must be created by an administrator of the Google Workspace. Please make sure to grant the following OAuth scopes to the service user:

1. `https://www.googleapis.com/auth/admin.directory.user.readonly`
2. `https://www.googleapis.com/auth/admin.directory.group.readonly`

At the end of this process, you should have JSON credentials to this Google Service Account.

You should now be ready to use the Google Directory connector in Airbyte.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                      |
| :------ | :--------- | :------------------------------------------------------- | :----------------------------------------------------------- |
| 0.2.29 | 2025-01-11 | [51098](https://github.com/airbytehq/airbyte/pull/51098) | Update dependencies |
| 0.2.28 | 2025-01-04 | [50925](https://github.com/airbytehq/airbyte/pull/50925) | Update dependencies |
| 0.2.27 | 2024-12-28 | [50578](https://github.com/airbytehq/airbyte/pull/50578) | Update dependencies |
| 0.2.26 | 2024-12-21 | [49987](https://github.com/airbytehq/airbyte/pull/49987) | Update dependencies |
| 0.2.25 | 2024-12-14 | [49168](https://github.com/airbytehq/airbyte/pull/49168) | Update dependencies |
| 0.2.24 | 2024-11-25 | [48638](https://github.com/airbytehq/airbyte/pull/48638) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.2.23 | 2024-10-29 | [47736](https://github.com/airbytehq/airbyte/pull/47736) | Update dependencies |
| 0.2.22 | 2024-10-22 | [47071](https://github.com/airbytehq/airbyte/pull/47071) | Update dependencies |
| 0.2.21 | 2024-10-12 | [46785](https://github.com/airbytehq/airbyte/pull/46785) | Update dependencies |
| 0.2.20 | 2024-10-05 | [46422](https://github.com/airbytehq/airbyte/pull/46422) | Update dependencies |
| 0.2.19 | 2024-09-28 | [46136](https://github.com/airbytehq/airbyte/pull/46136) | Update dependencies |
| 0.2.18 | 2024-09-21 | [45733](https://github.com/airbytehq/airbyte/pull/45733) | Update dependencies |
| 0.2.17 | 2024-09-14 | [45540](https://github.com/airbytehq/airbyte/pull/45540) | Update dependencies |
| 0.2.16 | 2024-09-07 | [45268](https://github.com/airbytehq/airbyte/pull/45268) | Update dependencies |
| 0.2.15 | 2024-08-31 | [45006](https://github.com/airbytehq/airbyte/pull/45006) | Update dependencies |
| 0.2.14 | 2024-08-24 | [44625](https://github.com/airbytehq/airbyte/pull/44625) | Update dependencies |
| 0.2.13 | 2024-08-17 | [44243](https://github.com/airbytehq/airbyte/pull/44243) | Update dependencies |
| 0.2.12 | 2024-08-10 | [43480](https://github.com/airbytehq/airbyte/pull/43480) | Update dependencies |
| 0.2.11 | 2024-08-03 | [43089](https://github.com/airbytehq/airbyte/pull/43089) | Update dependencies |
| 0.2.10 | 2024-07-27 | [42615](https://github.com/airbytehq/airbyte/pull/42615) | Update dependencies |
| 0.2.9 | 2024-07-20 | [42191](https://github.com/airbytehq/airbyte/pull/42191) | Update dependencies |
| 0.2.8 | 2024-07-13 | [41704](https://github.com/airbytehq/airbyte/pull/41704) | Update dependencies |
| 0.2.7 | 2024-07-10 | [41468](https://github.com/airbytehq/airbyte/pull/41468) | Update dependencies |
| 0.2.6 | 2024-07-09 | [41233](https://github.com/airbytehq/airbyte/pull/41233) | Update dependencies |
| 0.2.5 | 2024-07-06 | [40948](https://github.com/airbytehq/airbyte/pull/40948) | Update dependencies |
| 0.2.4 | 2024-06-25 | [40319](https://github.com/airbytehq/airbyte/pull/40319) | Update dependencies |
| 0.2.3 | 2024-06-22 | [39961](https://github.com/airbytehq/airbyte/pull/39961) | Update dependencies |
| 0.2.2 | 2024-05-20 | [38449](https://github.com/airbytehq/airbyte/pull/38449) | [autopull] base image + poetry + up_to_date |
| 0.2.1 | 2023-05-30 | [27236](https://github.com/airbytehq/airbyte/pull/27236) | Autoformat code |
| 0.2.0 | 2023-05-30 | [26775](https://github.com/airbytehq/airbyte/pull/26775) | Remove `authSpecification` from spec; update stream schemas. |
| 0.1.9 | 2021-12-06 | [8524](https://github.com/airbytehq/airbyte/pull/8524) | Update connector fields title/description |
| 0.1.8 | 2021-11-02 | [7409](https://github.com/airbytehq/airbyte/pull/7409) | Support oauth (update publish) |
| 0.1.7 | 2021-11-02 | [7409](https://github.com/airbytehq/airbyte/pull/7409) | Support oauth |
| 0.1.6 | 2021-11-02 | [7464](https://github.com/airbytehq/airbyte/pull/7464) | Migrate to the CDK |
| 0.1.5 | 2021-10-20 | [6930](https://github.com/airbytehq/airbyte/pull/6930) | Fix crash when a group don't have members |
| 0.1.4 | 2021-10-19 | [7167](https://github.com/airbytehq/airbyte/pull/7167) | Add organizations and phones to `users` schema |

</details>
