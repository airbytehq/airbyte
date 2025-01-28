# TrustPilot

## Prerequisites

- Trustpilot API Token or Zendesk OAuth 2.0 redentials
- Trustpilot Business Unit URLs

## Authentication methods

You can either authenticate with API key or with OAuth 2.0. Setting up OAuth 2.0 is a bit more complex but will give you access to more streams.

## Setup guide

### Step 1: Set up your Trustpilot App

Create a Trustpilot App as described in [Trustpilot docs](https://support.trustpilot.com/hc/en-us/articles/207309867-Getting-started-with-Trustpilot-s-APIs).

Enter the API key in the Airbyte source configuration "API key". In case you want to use OAuth 2.0 authentication, copy the API secret as well.

### Step 2: Requesting OAuth 2.0 refresh token (Optional)

Request the OAuth 2.0 request token by sending the following HTTP request:

```http
GET https://api.trustpilot.com/v1/oauth/oauth-business-users-for-applications/accesstoken
Authorization: Basic base64(apikey:secret)
Content-Type: application/x-www-form-urlencoded

grant_type=password&username=YOUR_TRUSTPILOT_USERNAME_OR_LOGIN_EMAIL_HERE&password=YOUR_TRUSTPILOT_PASSWORD_HERE
```

When succeeded, it will return a json object. Extrat the properties `access_token`, `refresh_token`.

Fill now the missing configuration fields in the Airbyte source configuration. As token expiry date, use the current time + 4 days (or calculate it yourself by calculating the date time of request add the seconds given in property `expires_in`).

## Supported sync modes

The **Trustpilot** source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- Full Refresh
- Incremental Sync

## Supported Streams

This Source is capable of syncing the following Streams:

- [Configured Business Units](<https://documentation-apidocumentation.trustpilot.com/business-units-api-(public)#find-a-business-unit>) - loads business units defined in the configuration
- [Business Units](<https://documentation-apidocumentation.trustpilot.com/business-units-api-(public)#get-a-list-of-all-business-units>) - loads **all** business units
- [Private Reviews](https://documentation-apidocumentation.trustpilot.com/business-units-api#business-unit-private-reviews) \(Incremental sync\)

## Performance considerations

The connector is restricted by Trustpilot [rate limit guidelines](https://documentation-apidocumentation.trustpilot.com/#LimitRates).

The Trustpilot connector should not run into any limits under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject         |
| :------ | :--------- | :------------------------------------------------------- | :-------------- |
| 0.3.9 | 2025-01-25 | [52408](https://github.com/airbytehq/airbyte/pull/52408) | Update dependencies |
| 0.3.8 | 2025-01-18 | [52025](https://github.com/airbytehq/airbyte/pull/52025) | Update dependencies |
| 0.3.7 | 2025-01-11 | [51413](https://github.com/airbytehq/airbyte/pull/51413) | Update dependencies |
| 0.3.6 | 2024-12-28 | [50751](https://github.com/airbytehq/airbyte/pull/50751) | Update dependencies |
| 0.3.5 | 2024-12-21 | [50371](https://github.com/airbytehq/airbyte/pull/50371) | Update dependencies |
| 0.3.4 | 2024-12-14 | [49751](https://github.com/airbytehq/airbyte/pull/49751) | Update dependencies |
| 0.3.3 | 2024-12-12 | [48193](https://github.com/airbytehq/airbyte/pull/48193) | Update dependencies |
| 0.3.2 | 2024-10-29 | [47937](https://github.com/airbytehq/airbyte/pull/47937) | Update dependencies |
| 0.3.1 | 2024-10-28 | [47647](https://github.com/airbytehq/airbyte/pull/47647) | Update dependencies |
| 0.3.0 | 2024-10-06 | [46529](https://github.com/airbytehq/airbyte/pull/46529) | Migrate to Manifest-only |
| 0.2.13 | 2024-10-05 | [46507](https://github.com/airbytehq/airbyte/pull/46507) | Update dependencies |
| 0.2.12 | 2024-09-28 | [46134](https://github.com/airbytehq/airbyte/pull/46134) | Update dependencies |
| 0.2.11 | 2024-09-21 | [45789](https://github.com/airbytehq/airbyte/pull/45789) | Update dependencies |
| 0.2.10 | 2024-09-14 | [45558](https://github.com/airbytehq/airbyte/pull/45558) | Update dependencies |
| 0.2.9 | 2024-09-07 | [45227](https://github.com/airbytehq/airbyte/pull/45227) | Update dependencies |
| 0.2.8 | 2024-08-31 | [45007](https://github.com/airbytehq/airbyte/pull/45007) | Update dependencies |
| 0.2.7 | 2024-08-24 | [44686](https://github.com/airbytehq/airbyte/pull/44686) | Update dependencies |
| 0.2.6 | 2024-08-17 | [44253](https://github.com/airbytehq/airbyte/pull/44253) | Update dependencies |
| 0.2.5 | 2024-08-12 | [43819](https://github.com/airbytehq/airbyte/pull/43819) | Update dependencies |
| 0.2.4 | 2024-08-10 | [43618](https://github.com/airbytehq/airbyte/pull/43618) | Update dependencies |
| 0.2.3 | 2024-08-03 | [43213](https://github.com/airbytehq/airbyte/pull/43213) | Update dependencies |
| `0.2.2` | 2024-08-05 | [42855](https://github.com/airbytehq/airbyte/pull/42855) | Fix refresh token URL |
| `0.2.1` | 2024-07-27 | [40267](https://github.com/airbytehq/airbyte/pull/40267) | Update dependencies |
| `0.2.0` | 2024-08-01 | [36200](https://github.com/airbytehq/airbyte/pull/36200) | Migrate to Low Code                               |
| `0.1.1` | 2024-05-21 | [38487](https://github.com/airbytehq/airbyte/pull/38487) | [autopull] base image + poetry + up_to_date |
| `0.1.0` | 2023-03-16 | [24009](https://github.com/airbytehq/airbyte/pull/24009) | Initial version |

</details>
