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
