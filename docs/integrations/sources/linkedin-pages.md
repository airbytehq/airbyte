# LinkedIn Pages

## Sync overview

The LinkedIn Pages source only supports Full Refresh for now. Incremental Sync will be coming soon.

Airbyte uses [LinkedIn Marketing Developer Platform - API](https://docs.microsoft.com/en-us/linkedin/marketing/integrations/marketing-integrations-overview) to fetch data from LinkedIn Pages.

### Output schema

This Source is capable of syncing the following data as streams:

* [Organization Lookup](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/organizations/organization-lookup-api?view=li-lms-2024-03&tabs=http#retrieve-organizations)
* [Follower Statistics](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/organizations/follower-statistics?view=li-lms-2024-03&tabs=http)
* [Share Statistics](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/organizations/share-statistics?view=li-lms-2024-03&tabs=http)
* [Total Follower Count](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/organizations/organization-lookup-api?view=li-lms-2024-03&tabs=http#retrieve-organization-follower-count)
* [Follower Statistics Time Bound (Incremental)](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/organizations/follower-statistics?view=li-lms-2024-03&tabs=http#retrieve-time-bound-follower-statistics)
* [Share Statistics Time Bound (Incremental)](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/organizations/share-statistics?view=li-lms-2024-03&tabs=http#retrieve-time-bound-share-statistics)

### Data type mapping

| Integration Type | Airbyte Type | Notes                      |
| :--------------- | :----------- | :------------------------- |
| `number`         | `number`     | float number               |
| `integer`        | `integer`    | whole number               |
| `array`          | `array`      |                            |
| `boolean`        | `boolean`    | True/False                 |
| `string`         | `string`     |                            |

### Features

| Feature                                   | Supported?\(Yes/No\) | Notes |
| :---------------------------------------- |:---------------------| :---- |
| Full Refresh Overwrite Sync               | Yes                  |       |
| Full Refresh Append Sync                  | No                   |       |
| Incremental - Append Sync                 | Yes                  |       |
| Incremental - Append + Deduplication Sync | No                   |       |
| Namespaces                                | No                   |       |

### Performance considerations

There are official Rate Limits for LinkedIn Pages API Usage, [more information here](https://learn.microsoft.com/en-us/linkedin/shared/api-guide/concepts/rate-limits?toc=%2Flinkedin%2Fmarketing%2Ftoc.json&bc=%2Flinkedin%2Fbreadcrumb%2Ftoc.json&view=li-lms-2024-03). Rate limited requests will receive a 429 response. Rate limits specify the maximum number of API calls that can be made in a 24 hour period. These limits reset at midnight UTC every day. In rare cases, LinkedIn may also return a 429 response as part of infrastructure protection. API service will return to normal automatically. In such cases you will receive the next error message:

```text
"Caught retryable error '<some_error> or null' after <some_number> tries. Waiting <some_number> seconds then retrying..."
```

This is expected when the connector hits the 429 - Rate Limit Exceeded HTTP Error. If the maximum of available API requests capacity is reached, you will have the following message:

```text
"Max try rate limit exceeded..."
```

After 5 unsuccessful attempts - the connector will stop the sync operation. In such cases check your Rate Limits [on this page](https://www.linkedin.com/developers/apps) &gt; Choose your app &gt; Analytics. 

## Getting started

The API user account should be assigned the following permissions for the API endpoints:
Endpoints such as: `Organization Lookup API`, `Follower Statistics`, `Share Statistics`, `Total Follower Count`, `Follower Statistics Time Bound`, `Share Statistics Time Bound` require these permissions:
* `r_organization_social`: Retrieve your organization's posts, comments, reactions, and other engagement data.
* `rw_organization_admin`: Manage your organization's pages and retrieve reporting data.

The API user account should be assigned the `ADMIN` role.

### Authentication

There are 2 authentication methods: Access Token or OAuth2.0.
OAuth2.0 is recommended since it will continue streaming data for 12 months instead of 2 months with an access token.

##### Create the `Refresh_Token` or `Access_Token`:
The source LinkedIn Pages can use either the `client_id`, `client_secret` and `refresh_token` for OAuth2.0 authentication or simply use an `access_token` in the UI connector's settings to make API requests. Access tokens expire after `2 months from creation date (60 days)` and require a user to manually authenticate again. Refresh tokens expire after `12 months from creation date (365 days)`. If you receive a `401 invalid token response`, the error logs will state that your token has expired and to re-authenticate your connection to generate a new token. This is described more [here](https://learn.microsoft.com/en-us/linkedin/shared/authentication/authorization-code-flow?toc=%2Flinkedin%2Fmarketing%2Ftoc.json&bc=%2Flinkedin%2Fbreadcrumb%2Ftoc.json&view=li-lms-2024-03&tabs=HTTPS1).

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

   * Navigate to the **Products** tab
   * Select the [Advertising API](https://learn.microsoft.com/en-us/linkedin/marketing/overview?view=li-lms-2024-03#advertising-api) and agree to the legal terms
   * After a few minutes, refresh the page to see a link to `View access form` in place of the **Select** button
   * Fill out the access form and access should be granted **within 72 hours** (usually quicker)

5. **Create A Refresh Token** (or Access Token):
   * Navigate to the LinkedIn Developers' [OAuth Token Tools](https://www.linkedin.com/developers/tools/oauth) and click **Create token**
   * Select your newly created app and check the boxes for the following scopes:
     * `r_organization_social`
     * `rw_organization_admin`
   * Click **Request access token** and once generated, **save your Refresh token**

6. **Use the `client_id`, `client_secret` and `refresh_token`** from Steps 2 and 5 to autorize the LinkedIn Pages connector within the Airbyte UI.
   * As mentioned earlier, you can also simply use the Access token auth method for 60-day access.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                              |
|:--------|:-----------| :------------------------------------------------------- | :--------------------------------------------------- |
| 1.1.9 | 2025-01-11 | [51149](https://github.com/airbytehq/airbyte/pull/51149) | Update dependencies |
| 1.1.8 | 2024-12-28 | [50645](https://github.com/airbytehq/airbyte/pull/50645) | Update dependencies |
| 1.1.7 | 2024-12-21 | [50114](https://github.com/airbytehq/airbyte/pull/50114) | Update dependencies |
| 1.1.6 | 2024-12-14 | [49593](https://github.com/airbytehq/airbyte/pull/49593) | Update dependencies |
| 1.1.5 | 2024-12-12 | [49272](https://github.com/airbytehq/airbyte/pull/49272) | Update dependencies |
| 1.1.4 | 2024-12-11 | [48924](https://github.com/airbytehq/airbyte/pull/48924) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 1.1.3 | 2024-10-29 | [47749](https://github.com/airbytehq/airbyte/pull/47749) | Update dependencies |
| 1.1.2 | 2024-10-28 | [47455](https://github.com/airbytehq/airbyte/pull/47455) | Update dependencies |
| 1.1.1 | 2024-08-16 | [44196](https://github.com/airbytehq/airbyte/pull/44196) | Bump source-declarative-manifest version |
| 1.1.0 | 2024-08-15 | [44132](https://github.com/airbytehq/airbyte/pull/44132) | Refactor connector to manifest-only format |
| 1.0.17 | 2024-08-10 | [43560](https://github.com/airbytehq/airbyte/pull/43560) | Update dependencies |
| 1.0.16 | 2024-08-03 | [43281](https://github.com/airbytehq/airbyte/pull/43281) | Update dependencies |
| 1.0.15 | 2024-07-27 | [42782](https://github.com/airbytehq/airbyte/pull/42782) | Update dependencies |
| 1.0.14 | 2024-07-20 | [42218](https://github.com/airbytehq/airbyte/pull/42218) | Update dependencies |
| 1.0.13 | 2024-07-13 | [41833](https://github.com/airbytehq/airbyte/pull/41833) | Update dependencies |
| 1.0.12 | 2024-07-10 | [41407](https://github.com/airbytehq/airbyte/pull/41407) | Update dependencies |
| 1.0.11 | 2024-07-09 | [41274](https://github.com/airbytehq/airbyte/pull/41274) | Update dependencies |
| 1.0.10 | 2024-07-06 | [40828](https://github.com/airbytehq/airbyte/pull/40828) | Update dependencies |
| 1.0.9 | 2024-06-25 | [40422](https://github.com/airbytehq/airbyte/pull/40422) | Update dependencies |
| 1.0.8 | 2024-06-22 | [39975](https://github.com/airbytehq/airbyte/pull/39975) | Update dependencies |
| 1.0.7 | 2024-06-13 | [36744](https://github.com/airbytehq/airbyte/pull/36744) | Add time bound incremental streams for follower & share statistics. Migrate to Low Code |
| 1.0.6 | 2024-06-06 | [39171](https://github.com/airbytehq/airbyte/pull/39171) | [autopull] Upgrade base image to v1.2.2 |
| 1.0.5 | 2024-06-03 | [38918](https://github.com/airbytehq/airbyte/pull/38918) | Replace AirbyteLogger with logging.Logger |
| 1.0.4 | 2024-06-03 | [38918](https://github.com/airbytehq/airbyte/pull/38918) | Replace AirbyteLogger with logging.Logger |
| 1.0.3 | 2024-05-21 | [38526](https://github.com/airbytehq/airbyte/pull/38526) | [autopull] base image + poetry + up_to_date |
| 1.0.2 | 2023-05-30 | [24352](https://github.com/airbytehq/airbyte/pull/24352) | Remove duplicate streams |
| 1.0.1 | 2023-03-22 | [24352](https://github.com/airbytehq/airbyte/pull/24352) | Remove `authSpecification` as it's not yet supported |
| 1.0.0 | 2023-03-16 | [18967](https://github.com/airbytehq/airbyte/pull/18967) | Fixed failing connection checks |
| 0.1.0 | 2022-08-11 | [13098](https://github.com/airbytehq/airbyte/pull/13098) | Initial Release |

</details>
