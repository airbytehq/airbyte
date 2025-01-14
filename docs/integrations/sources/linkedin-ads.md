# LinkedIn Ads

<HideInUI>

This page contains the setup guide and reference information for the [LinkedIn Ads](https://learn.microsoft.com/en-us/linkedin/) source connector.

</HideInUI>

## Prerequisites

- A LinkedIn Ads account with permission to access data from accounts you want to sync.
- Start Date - a date programmatically in the format YYYY-MM-DD. Any data before this date will not be replicated.

## Setup guide

### Step 1: Set up LinkedIn Ads

<!-- env:cloud -->

We recommend using **Oauth2.0** authentication for Airbyte Cloud, as this significantly simplifies the setup process, and allows you to authenticate your account directly from the Airbyte UI.

<!-- /env:cloud -->

<!-- env:oss -->

### Set up LinkedIn Ads authentication (Airbyte Open Source)

To authenticate the connector in Airbyte Open Source, you will need to create a Linkedin developer application and obtain one of the following credentials:

1. OAuth2.0 credentials, consisting of:

   - Client ID
   - Client Secret
   - Refresh Token (expires after 12 months)

2. Access Token (expires after 60 days)

You can follow the steps laid out below to create the application and obtain the necessary credentials. For an overview of the LinkedIn authentication process, see the [official documentation](https://learn.microsoft.com/en-us/linkedin/shared/authentication/authentication?context=linkedin%2Fcontext).

#### Create a LinkedIn developer application

1. [Log in to LinkedIn](https://developer.linkedin.com/) with a developer account.
2. Navigate to the [Apps page](https://www.linkedin.com/developers/apps) and click the **Create App** icon. Fill in the fields below:

   1. For **App Name**, enter a name.
   2. For **LinkedIn Page**, enter your company's name or LinkedIn Company Page URL.
   3. For **Privacy policy URL**, enter the link to your company's privacy policy.
   4. For **App logo**, upload your company's logo.
   5. Check **I have read and agree to these terms**, then click **Create App**. LinkedIn redirects you to a page showing the details of your application.

3. You can verify your app using the following steps:

   1. Click the **Settings** tab. On the **App Settings** section, click **Verify** under **Company**. A popup window will be displayed. To generate the verification URL, click on **Generate URL**, then copy and send the URL to the Page Admin (this may be you). Click on **I'm done**. If you are the administrator of your Page, simply run the URL in a new tab (if not, an administrator will have to do the next step). Click on **Verify**.

   2. To display the Products page, click the **Product** tab. For **Marketing Developer Platform**, click **Request access**. A popup window will be displayed. Review and Select **I have read and agree to these terms**. Finally, click **Request access**.

#### Authorize your app

1. To authorize your application, click the **Auth** tab. Copy the **Client ID** and **Client Secret** (click the open eye icon to reveal the client secret). In the **Oauth 2.0 settings**, click the pencil icon and provide a redirect URL for your app.

2. Click the **OAuth 2.0 tools** link in the **Understanding authentication and OAuth 2.0** section on the right side of the page.
3. Click **Create token**.
4. Select the scopes you want to use for your app. We recommend using the following scopes:
   - `r_emailaddress`
   - `r_liteprofile`
   - `r_ads`
   - `r_ads_reporting`
   - `r_organization_social`
5. Click **Request access token**. You will be redirected to an authorization page. Use your LinkedIn credentials to log in and authorize your app and obtain your **Access Token** and **Refresh Token**.

:::caution
These tokens will not be displayed again, so make sure to copy them and store them securely.
:::

:::tip
If either of your tokens expire, you can generate new ones by returning to LinkedIn's [Token Generator](https://www.linkedin.com/developers/tools/oauth/token-generator). You can also check on the status of your tokens using the [Token Inspector](https://www.linkedin.com/developers/tools/oauth/token-inspector).
:::

<!-- /env:oss -->

### Step 2: Set up the LinkedIn Ads connector in Airbyte


<!-- env:cloud -->

#### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. Click Sources and then click + New source.
3. On the Set up the source page, select LinkedIn Ads from the Source type dropdown.
4. Enter a name for the LinkedIn Ads connector.
5. To authenticate:

- Select **OAuth2.0** from the Authentication dropdown, then click **Authenticate your LinkedIn Ads account**. Sign in to your account and click **Allow**.
<!-- /env:cloud -->

<!-- env:oss -->

#### For Airbyte Open Source:

1. Navigate to the Airbyte Open Source dashboard.
2. Click Sources and then click + New source.
3. On the Set up the source page, select LinkedIn Ads from the Source type dropdown.
4. Enter a name for the LinkedIn Ads connector.
5. To authenticate:
- Select an option from the Authentication dropdown:
  1. **OAuth2.0:** Enter your **Client ID**, **Client Secret** and **Refresh Token**. Please note that the refresh token expires after 12 months.
  2. **Access Token:** Enter your **Access Token**. Please note that the access token expires after 60 days.
  <!-- /env:oss -->

6. For **Start Date**, use the provided datepicker or enter a date programmatically in the format YYYY-MM-DD. Any data before this date will not be replicated.
7. (Optional) For **Account IDs**, you may optionally provide a space separated list of Account IDs to pull data from. If you do not specify any account IDs, the connector will replicate data from all accounts accessible using your credentials.
8. (Optional) For **Custom Ad Analytics Reports**, you may optionally provide one or more custom reports to query the LinkedIn Ads API for. By defining custom reports, you can better align the data pulled form LinkedIn Ads with your particular needs. To add a custom report:
   1. Click on **Add**.
   2. Enter a **Report Name**. This will be used as the stream name during replication.
   3. Select a **Pivot Category** from the dropdown. This defines the main dimension by which the report data will be grouped or segmented.
   4. Select a **Time Granularity** to group the data in your report by time. The options are:
      - `ALL`: Data is not grouped by time, providing a cumulative view.
      - `DAILY`: Returns data grouped by day. Useful for closely monitoring short-term changes and effects.
      - `MONTHLY`: Returns data grouped by month. Ideal for evaluating monthly goals or observing seasonal patterns.
      - `YEARLY`: Returns data grouped by year. Ideal for high-level analysis of long-term trends and year-over-year comparisons.
9. Click **Set up source** and wait for the tests to complete.
<!-- /env:cloud -->

## Supported sync modes

The LinkedIn Ads source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts/#connection-sync-modes):

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
- [Incremental Sync - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
- [Incremental Sync - Append + Deduped](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append-deduped)

## Supported Streams

- [Accounts](https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads/account-structure/create-and-manage-accounts?tabs=http&view=li-lms-2023-05#search-for-accounts)
- [Account Users](https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads/account-structure/create-and-manage-account-users?tabs=http&view=li-lms-2023-05#find-ad-account-users-by-accounts)
- [Campaign Groups](https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads/account-structure/create-and-manage-campaign-groups?tabs=http&view=li-lms-2023-05#search-for-campaign-groups)
- [Campaigns](https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads/account-structure/create-and-manage-campaigns?tabs=http&view=li-lms-2023-05#search-for-campaigns)
- [Creatives](https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads/account-structure/create-and-manage-creatives?tabs=http%2Chttp-update-a-creative&view=li-lms-2023-05#search-for-creatives)
- [Conversions](https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads-reporting/conversion-tracking?view=li-lms-2023-05&tabs=curl#find-conversions-by-ad-account)
- [Ad Analytics by Campaign](https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads-reporting/ads-reporting?tabs=curl&view=li-lms-2023-05#ad-analytics)
- [Ad Analytics by Creative](https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads-reporting/ads-reporting?tabs=curl&view=li-lms-2023-05#ad-analytics)
- [Ad Analytics by Impression Device](https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads-reporting/ads-reporting?tabs=curl&view=li-lms-2023-05#ad-analytics)
- [Ad Analytics by Member Company Size](https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads-reporting/ads-reporting?tabs=curl&view=li-lms-2023-05#ad-analytics)
- [Ad Analytics by Member Country](https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads-reporting/ads-reporting?tabs=curl&view=li-lms-2023-05#ad-analytics)
- [Ad Analytics by Member Job Function](https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads-reporting/ads-reporting?tabs=curl&view=li-lms-2023-05#ad-analytics)
- [Ad Analytics by Member Job Title](https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads-reporting/ads-reporting?tabs=curl&view=li-lms-2023-05#ad-analytics)
- [Ad Analytics by Member Industry](https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads-reporting/ads-reporting?tabs=curl&view=li-lms-2023-05#ad-analytics)
- [Ad Analytics by Member Region](https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads-reporting/ads-reporting?tabs=curl&view=li-lms-2023-05#ad-analytics)
- [Ad Analytics by Member Company](https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads-reporting/ads-reporting?tabs=curl&view=li-lms-2023-05#ad-analytics)

:::info

For Ad Analytics Streams such as `Ad Analytics by Campaign` and `Ad Analytics by Creative`, the `pivot` column name is renamed to `pivotValue` to handle the data normalization correctly and avoid name conflicts with certain destinations. This field contains the ID of the associated entity as a [URN](https://learn.microsoft.com/en-us/linkedin/shared/api-guide/concepts/urns). Please refer to the [LinkedIn documentation](https://learn.microsoft.com/en-us/linkedin/marketing/urn-resolution?view=li-lms-2023-05) for the format of the URN value for the Ad Analytics streams.

:::

## Performance considerations

LinkedIn Ads has Official Rate Limits for API Usage, [more information here](https://docs.microsoft.com/en-us/linkedin/shared/api-guide/concepts/rate-limits?context=linkedin/marketing/context). Rate limited requests will receive a 429 response. These limits reset at midnight UTC every day. In rare cases, LinkedIn may also return a 429 response as part of infrastructure protection. API service will return to normal automatically. In such cases, you will receive the following error message:

```text
"Caught retriable error '<some_error> or null' after <some_number> tries. Waiting <some_number> seconds then retrying..."
```

This is expected when the connector hits the 429 - Rate Limit Exceeded HTTP Error. If the maximum available API requests capacity is reached, you will have the following message:

```text
"Max try rate limit exceeded..."
```

After 5 unsuccessful attempts - the connector will stop the sync operation. In such cases check your Rate Limits [on this page](https://www.linkedin.com/developers/apps) &gt; Choose your app &gt; Analytics.

## Data type map

| Integration Type | Airbyte Type | Notes                       |
|:-----------------|:-------------|:----------------------------|
| `number`         | `number`     | float number                |
| `integer`        | `integer`    | whole number                |
| `date`           | `string`     | FORMAT YYYY-MM-DD           |
| `datetime`       | `string`     | FORMAT YYYY-MM-DDThh:mm: ss |
| `array`          | `array`      |                             |
| `boolean`        | `boolean`    | True/False                  |
| `string`         | `string`     |                             |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                                                         |
|:--------|:-----------|:---------------------------------------------------------|:----------------------------------------------------------------------------------------------------------------|
| 5.1.0   | 2025-01-14 | [48863](https://github.com/airbytehq/airbyte/pull/48863) | Custom streams moved to manifest implementation                                                                 |
| 5.0.0   | 2024-11-26 | [48451](https://github.com/airbytehq/airbyte/pull/48451) | Update primary keys for streams ad_campaign_analytics, Custom Ad Analytics Reports and account_users            |
| 4.1.4   | 2024-10-12 | [46862](https://github.com/airbytehq/airbyte/pull/46862) | Update dependencies                                                                                             |
| 4.1.3   | 2024-10-05 | [46433](https://github.com/airbytehq/airbyte/pull/46433) | Update dependencies                                                                                             |
| 4.1.2   | 2024-09-28 | [46171](https://github.com/airbytehq/airbyte/pull/46171) | Update dependencies                                                                                             |
| 4.1.1   | 2024-09-21 | [45774](https://github.com/airbytehq/airbyte/pull/45774) | Update dependencies                                                                                             |
| 4.1.0   | 2024-09-20 | [44370](https://github.com/airbytehq/airbyte/pull/44370) | Migrate to low-code                                                                                             |
| 4.0.6   | 2024-09-14 | [45532](https://github.com/airbytehq/airbyte/pull/45532) | Update dependencies                                                                                             |
| 4.0.5   | 2024-09-07 | [45209](https://github.com/airbytehq/airbyte/pull/45209) | Update dependencies                                                                                             |
| 4.0.4   | 2024-08-31 | [44950](https://github.com/airbytehq/airbyte/pull/44950) | Update dependencies                                                                                             |
| 4.0.3   | 2024-08-24 | [44682](https://github.com/airbytehq/airbyte/pull/44682) | Update dependencies                                                                                             |
| 4.0.2   | 2024-08-17 | [44220](https://github.com/airbytehq/airbyte/pull/44220) | Update dependencies                                                                                             |
| 4.0.1   | 2024-08-10 | [43629](https://github.com/airbytehq/airbyte/pull/43629) | Update dependencies                                                                                             |
| 4.0.0   | 2024-08-07 | [43359](https://github.com/airbytehq/airbyte/pull/43359) | Revert low code migration                                                                                       |
| 3.0.1   | 2024-08-03 | [43087](https://github.com/airbytehq/airbyte/pull/43087) | Update dependencies                                                                                             |
| 3.0.0   | 2024-06-18 | [38314](https://github.com/airbytehq/airbyte/pull/38314) | Migrate to low-code                                                                                             |
| 2.1.12  | 2024-07-27 | [42728](https://github.com/airbytehq/airbyte/pull/42728) | Update dependencies                                                                                             |
| 2.1.11  | 2024-07-20 | [42291](https://github.com/airbytehq/airbyte/pull/42291) | Update dependencies                                                                                             |
| 2.1.10  | 2024-07-13 | [41710](https://github.com/airbytehq/airbyte/pull/41710) | Update dependencies                                                                                             |
| 2.1.9   | 2024-07-10 | [41517](https://github.com/airbytehq/airbyte/pull/41517) | Update dependencies                                                                                             |
| 2.1.8   | 2024-07-09 | [41315](https://github.com/airbytehq/airbyte/pull/41315) | Update dependencies                                                                                             |
| 2.1.7   | 2024-07-06 | [40868](https://github.com/airbytehq/airbyte/pull/40868) | Update dependencies                                                                                             |
| 2.1.6   | 2024-06-25 | [40331](https://github.com/airbytehq/airbyte/pull/40331) | Update dependencies                                                                                             |
| 2.1.5   | 2024-06-22 | [39998](https://github.com/airbytehq/airbyte/pull/39998) | Update dependencies                                                                                             |
| 2.1.4   | 2024-06-16 | [39442](https://github.com/airbytehq/airbyte/pull/39442) | Fix README commands, change spec from json to yaml, fix schema states to object                                 |
| 2.1.3   | 2024-06-06 | [39240](https://github.com/airbytehq/airbyte/pull/39240) | [autopull] Upgrade base image to v1.2.2                                                                         |
| 2.1.2   | 2024-05-07 | [36648](https://github.com/airbytehq/airbyte/pull/36648) | Schema descriptions                                                                                             |
| 2.1.1   | 2024-05-07 | [38013](https://github.com/airbytehq/airbyte/pull/38013) | Fix an issue where the `Accounts` stream did not correctly handle provided account IDs                          |
| 2.1.0   | 2024-04-30 | [37573](https://github.com/airbytehq/airbyte/pull/37573) | Update API version to `202404`; add cursor-based pagination                                                     |
| 2.0.0   | 2024-04-24 | [37531](https://github.com/airbytehq/airbyte/pull/37531) | Change primary key for Analytics Streams                                                                        |
| 1.0.1   | 2024-03-28 | [34152](https://github.com/airbytehq/airbyte/pull/34152) | Proceed pagination if return less than expected                                                                 |
| 1.0.0   | 2024-04-10 | [36927](https://github.com/airbytehq/airbyte/pull/36927) | Update primary key for Analytics Streams                                                                        |
| 0.8.0   | 2024-03-19 | [36267](https://github.com/airbytehq/airbyte/pull/36267) | Pin airbyte-cdk version to `^0`                                                                                 |
| 0.7.0   | 2024-02-20 | [35465](https://github.com/airbytehq/airbyte/pull/35465) | Per-error reporting and continue sync on stream failures                                                        |
| 0.6.8   | 2024-02-09 | [35086](https://github.com/airbytehq/airbyte/pull/35086) | Manage dependencies with Poetry                                                                                 |
| 0.6.7   | 2024-01-11 | [34152](https://github.com/airbytehq/airbyte/pull/34152) | Prepare for airbyte-lib                                                                                         |
| 0.6.6   | 2024-01-15 | [34222](https://github.com/airbytehq/airbyte/pull/34222) | Use stream slices for Analytics streams                                                                         |
| 0.6.5   | 2023-12-15 | [33530](https://github.com/airbytehq/airbyte/pull/33530) | Fix typo in `Pivot Category` list                                                                               |
| 0.6.4   | 2023-10-19 | [31599](https://github.com/airbytehq/airbyte/pull/31599) | Base image migration: remove Dockerfile and use the python-connector-base image                                 |
| 0.6.3   | 2023-10-13 | [31396](https://github.com/airbytehq/airbyte/pull/31396) | Fix pagination for reporting                                                                                    |
| 0.6.2   | 2023-08-23 | [31221](https://github.com/airbytehq/airbyte/pull/31221) | Increase max time between messages to 24 hours                                                                  |
| 0.6.1   | 2023-08-23 | [29600](https://github.com/airbytehq/airbyte/pull/29600) | Update field descriptions                                                                                       |
| 0.6.0   | 2023-08-22 | [29721](https://github.com/airbytehq/airbyte/pull/29721) | Add `Conversions` stream                                                                                        |
| 0.5.0   | 2023-08-14 | [29175](https://github.com/airbytehq/airbyte/pull/29175) | Add Custom report Constructor                                                                                   |
| 0.4.0   | 2023-08-08 | [29175](https://github.com/airbytehq/airbyte/pull/29175) | Add analytics streams                                                                                           |
| 0.3.1   | 2023-08-08 | [29189](https://github.com/airbytehq/airbyte/pull/29189) | Fix empty accounts field                                                                                        |
| 0.3.0   | 2023-08-07 | [29045](https://github.com/airbytehq/airbyte/pull/29045) | Add new fields to schemas; convert datetime fields to `rfc3339`                                                 |
| 0.2.1   | 2023-05-30 | [26780](https://github.com/airbytehq/airbyte/pull/26780) | Reduce records limit for Creatives Stream                                                                       |
| 0.2.0   | 2023-05-23 | [26372](https://github.com/airbytehq/airbyte/pull/26372) | Migrate to LinkedIn API version: May 2023                                                                       |
| 0.1.16  | 2023-05-24 | [26512](https://github.com/airbytehq/airbyte/pull/26512) | Removed authSpecification from spec.json in favour of advancedAuth                                              |
| 0.1.15  | 2023-02-13 | [22940](https://github.com/airbytehq/airbyte/pull/22940) | Specified date formatting in specification                                                                      |
| 0.1.14  | 2023-02-03 | [22361](https://github.com/airbytehq/airbyte/pull/22361) | Turn on default HttpAvailabilityStrategy                                                                        |
| 0.1.13  | 2023-01-27 | [22013](https://github.com/airbytehq/airbyte/pull/22013) | For adDirectSponsoredContents stream skip accounts which are part of organization                               |
| 0.1.12  | 2022-10-18 | [18111](https://github.com/airbytehq/airbyte/pull/18111) | For adDirectSponsoredContents stream skip accounts which are part of organization                               |
| 0.1.11  | 2022-10-07 | [17724](https://github.com/airbytehq/airbyte/pull/17724) | Retry 429/5xx errors when refreshing access token                                                               |
| 0.1.10  | 2022-09-28 | [17326](https://github.com/airbytehq/airbyte/pull/17326) | Migrate to per-stream states.                                                                                   |
| 0.1.9   | 2022-07-21 | [14924](https://github.com/airbytehq/airbyte/pull/14924) | Remove `additionalProperties` field from schemas                                                                |
| 0.1.8   | 2022-06-07 | [13495](https://github.com/airbytehq/airbyte/pull/13495) | Fixed `base-normalization` issue on `Destination Redshift` caused by wrong casting of `pivot` column            |
| 0.1.7   | 2022-05-04 | [12482](https://github.com/airbytehq/airbyte/pull/12482) | Update input configuration copy                                                                                 |
| 0.1.6   | 2022-04-04 | [11690](https://github.com/airbytehq/airbyte/pull/11690) | Small documentation corrections                                                                                 |
| 0.1.5   | 2021-12-21 | [8984](https://github.com/airbytehq/airbyte/pull/8984)   | Update connector fields title/description                                                                       |
| 0.1.4   | 2021-12-02 | [8382](https://github.com/airbytehq/airbyte/pull/8382)   | Modify log message in rate-limit cases                                                                          |
| 0.1.3   | 2021-11-11 | [7839](https://github.com/airbytehq/airbyte/pull/7839)   | Added OAuth support                                                                                             |
| 0.1.2   | 2021-11-08 | [7499](https://github.com/airbytehq/airbyte/pull/7499)   | Remove base-python dependencies                                                                                 |
| 0.1.1   | 2021-10-02 | [6610](https://github.com/airbytehq/airbyte/pull/6610)   | Fix for `Campaigns/targetingCriteria` transformation, coerced `Creatives/variables/values` to string by default |
| 0.1.0   | 2021-09-05 | [5285](https://github.com/airbytehq/airbyte/pull/5285)   | Initial release of Native LinkedIn Ads connector for Airbyte                                                    |

</details>
