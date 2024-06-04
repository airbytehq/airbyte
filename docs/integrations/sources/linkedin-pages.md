# LinkedIn Pages

## Sync overview

The LinkedIn Pages source only supports Full Refresh for now. Incremental Sync will be coming soon.

Airbyte uses [LinkedIn Marketing Developer Platform - API](https://docs.microsoft.com/en-us/linkedin/marketing/integrations/marketing-integrations-overview) to fetch data from LinkedIn Pages.

### Output schema

This Source is capable of syncing the following data as streams:

- [Organization Lookup](https://docs.microsoft.com/en-us/linkedin/marketing/integrations/community-management/organizations/organization-lookup-api?tabs=http#retrieve-organizations)
- [Follower Statistics](https://docs.microsoft.com/en-us/linkedin/marketing/integrations/community-management/organizations/follower-statistics?tabs=http#retrieve-lifetime-follower-statistics)
- [Page Statistics](https://docs.microsoft.com/en-us/linkedin/marketing/integrations/community-management/organizations/page-statistics?tabs=http#retrieve-lifetime-organization-page-statistics)
- [Share Statistics](https://docs.microsoft.com/en-us/linkedin/marketing/integrations/community-management/organizations/share-statistics?tabs=http#retrieve-lifetime-share-statistics)
- [Shares (Latest 50)](https://docs.microsoft.com/en-us/linkedin/marketing/integrations/community-management/shares/share-api?tabs=http#find-shares-by-owner)
- [Total Follower Count](https://docs.microsoft.com/en-us/linkedin/marketing/integrations/community-management/organizations/organization-lookup-api?tabs=http#retrieve-organization-follower-count)
- [UGC Posts](https://docs.microsoft.com/en-us/linkedin/marketing/integrations/community-management/shares/ugc-post-api?tabs=http#find-ugc-posts-by-authors)

### NOTE:

All streams only sync all-time statistics at this time. A `start_date` field will be added soon to pull data starting at a single point in time.

### Data type mapping

| Integration Type | Airbyte Type | Notes        |
| :--------------- | :----------- | :----------- |
| `number`         | `number`     | float number |
| `integer`        | `integer`    | whole number |
| `array`          | `array`      |              |
| `boolean`        | `boolean`    | True/False   |
| `string`         | `string`     |              |

### Features

| Feature                                   | Supported?\(Yes/No\) | Notes |
| :---------------------------------------- | :------------------- | :---- |
| Full Refresh Overwrite Sync               | Yes                  |       |
| Full Refresh Append Sync                  | No                   |       |
| Incremental - Append Sync                 | No                   |       |
| Incremental - Append + Deduplication Sync | No                   |       |
| Namespaces                                | No                   |       |

### Performance considerations

There are official Rate Limits for LinkedIn Pages API Usage, [more information here](https://docs.microsoft.com/en-us/linkedin/shared/api-guide/concepts/rate-limits?context=linkedin/marketing/context). Rate limited requests will receive a 429 response. Rate limits specify the maximum number of API calls that can be made in a 24 hour period. These limits reset at midnight UTC every day. In rare cases, LinkedIn may also return a 429 response as part of infrastructure protection. API service will return to normal automatically. In such cases you will receive the next error message:

```text
"Caught retryable error '<some_error> or null' after <some_number> tries. Waiting <some_number> seconds then retrying..."
```

This is expected when the connector hits the 429 - Rate Limit Exceeded HTTP Error. If the maximum of available API requests capacity is reached, you will have the following message:

```text
"Max try rate limit exceded..."
```

After 5 unsuccessful attempts - the connector will stop the sync operation. In such cases check your Rate Limits [on this page](https://www.linkedin.com/developers/apps) &gt; Choose your app &gt; Analytics.

## Getting started

The API user account should be assigned the following permissions for the API endpoints:
Endpoints such as: `Organization Lookup API`, `Follower Statistics`, `Page Statistics`, `Share Statistics`, `Shares`, `UGC Posts` require these permissions:

- `r_organization_social`: Retrieve your organization's posts, comments, reactions, and other engagement data.
- `rw_organization_admin`: Manage your organization's pages and retrieve reporting data.

The API user account should be assigned the `ADMIN` role.

### Authentication

There are 2 authentication methods: Access Token or OAuth2.0.
OAuth2.0 is recommended since it will continue streaming data for 12 months instead of 2 months with an access token.

##### Create the `Refresh_Token` or `Access_Token`:

The source LinkedIn Pages can use either the `client_id`, `client_secret` and `refresh_token` for OAuth2.0 authentication or simply use an `access_token` in the UI connector's settings to make API requests. Access tokens expire after `2 months from creation date (60 days)` and require a user to manually authenticate again. Refresh tokens expire after `12 months from creation date (365 days)`. If you receive a `401 invalid token response`, the error logs will state that your token has expired and to re-authenticate your connection to generate a new token. This is described more [here](https://docs.microsoft.com/en-us/linkedin/shared/authentication/authorization-code-flow?context=linkedin/context).

1. **Log in to LinkedIn as the API user**

2. **Create an App** [here](https://www.linkedin.com/developers/apps):

   - `App Name`: airbyte-source
   - `Company`: search and find your LinkedIn Company Page
   - `Privacy policy URL`: link to company privacy policy
   - `Business email`: developer/admin email address
   - `App logo`: Airbyte's \(or Company's\) logo
   - Review/agree to legal terms and create app
   - Review the **Auth** tab:
     - **Save your `client_id` and `client_secret`** \(for later steps\)
     - Oauth 2.0 settings: Provide a `redirect_uri` \(for later steps\): `https://airbyte.com`

3. **Verify App**:

   - In the **Settings** tab of your app dashboard, you'll see a **Verify** button. Click that button!
   - Generate and provide the verify URL to your Company's LinkedIn Admin to verify the app.

4. **Request API Access**:

   - Navigate to the **Products** tab
   - Select the [Marketing Developer Platform](https://docs.microsoft.com/en-us/linkedin/marketing/) and agree to the legal terms
   - After a few minutes, refresh the page to see a link to `View access form` in place of the **Select** button
   - Fill out the access form and access should be granted **within 72 hours** (usually quicker)

5. **Create A Refresh Token** (or Access Token):

   - Navigate to the LinkedIn Developers' [OAuth Token Tools](https://www.linkedin.com/developers/tools/oauth) and click **Create token**
   - Select your newly created app and check the boxes for the following scopes:
     - `r_organization_social`
     - `rw_organization_admin`
   - Click **Request access token** and once generated, **save your Refresh token**

6. **Use the `client_id`, `client_secret` and `refresh_token`** from Steps 2 and 5 to autorize the LinkedIn Pages connector within the Airbyte UI.
   - As mentioned earlier, you can also simply use the Access token auth method for 60-day access.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                              |
| :------ | :--------- | :------------------------------------------------------- | :--------------------------------------------------- |
| 1.0.5 | 2024-06-03 | [38918](https://github.com/airbytehq/airbyte/pull/38918) | Replace AirbyteLogger with logging.Logger |
| 1.0.4 | 2024-06-03 | [38918](https://github.com/airbytehq/airbyte/pull/38918) | Replace AirbyteLogger with logging.Logger |
| 1.0.3 | 2024-05-21 | [38526](https://github.com/airbytehq/airbyte/pull/38526) | [autopull] base image + poetry + up_to_date |
| 1.0.2 | 2023-05-30 | [24352](https://github.com/airbytehq/airbyte/pull/24352) | Remove duplicate streams |
| 1.0.1 | 2023-03-22 | [24352](https://github.com/airbytehq/airbyte/pull/24352) | Remove `authSpecification` as it's not yet supported |
| 1.0.0 | 2023-03-16 | [18967](https://github.com/airbytehq/airbyte/pull/18967) | Fixed failing connection checks |
| 0.1.0 | 2022-08-11 | [13098](https://github.com/airbytehq/airbyte/pull/13098) | Initial Release |

</details>