# LinkedIn Leads

This page contains the setup guide and reference information for the LinkedIn Leads source connector.

:::tip
Most of below prerequisites and authentication inputs are similar to [LinkedIn Ads source connector documentation](https://docs.airbyte.com/integrations/sources/linkedin-ads), as underlying API is the same one.  
A specific scope is mandatory for Leads: `r_marketing_leadgen_automation`.
:::

## Prerequisites

- A LinkedIn Ads account with permission to access data from accounts you want to sync.

## Setup guide

<!-- env:oss -->

### Set up authentication (Airbyte Open Source)

To authenticate the connector in Airbyte Open Source, you will need to create a LinkedIn developer application and obtain one of the following credentials:

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
   - `r_marketing_leadgen_automation`
   - `r_liteprofile`
   - `r_ads`
5. Click **Request access token**. You will be redirected to an authorization page. Use your LinkedIn credentials to log in and authorize your app and obtain your **Access Token** and **Refresh Token**.

:::caution
These tokens will not be displayed again, so make sure to copy them and store them securely.
:::

:::tip
If either of your tokens expire, you can generate new ones by returning to LinkedIn's [Token Generator](https://www.linkedin.com/developers/tools/oauth/token-generator). You can also check on the status of your tokens using the [Token Inspector](https://www.linkedin.com/developers/tools/oauth/token-inspector).
:::

<!-- /env:oss -->

### Set up the LinkedIn Leads connector in Airbyte

1. [Log in to your Airbyte Cloud](https://cloud.airbyte.com/workspaces) or Airbyte Open Source account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ New source**.
3. Find and select **LinkedIn Leads** from the list of available sources.
4. For **Source name**, enter a name for the LinkedIn Leads connector.
5. To authenticate:

<!-- env:cloud -->

#### For Airbyte Cloud

:::caution
It has not been tested yet.
:::
<!-- /env:cloud -->

<!-- env:oss -->

#### For Airbyte Open Source

- Select an option from the Authentication dropdown:
  1. **OAuth2.0:** Enter your **Client ID**, **Client Secret** and **Refresh Token**. Please note that the refresh token expires after 12 months.
  2. **Access Token:** Enter your **Access Token**. Please note that the access token expires after 60 days.
  <!-- /env:oss -->

6. For **Account IDs**, provide a space separated list of Account IDs to pull data from.
7. Click **Set up source** and wait for the tests to complete.
<!-- /env:cloud -->

## Supported sync modes

The LinkedIn Leads source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)

## Supported streams

- [Lead Forms](https://learn.microsoft.com/en-us/linkedin/marketing/lead-sync/leadsync?view=li-lms-2024-06&tabs=http#get-lead-forms)
- [Lead Forms Responses](https://learn.microsoft.com/en-us/linkedin/marketing/lead-sync/leadsync?view=li-lms-2024-06&tabs=http#get-lead-form-responses)

## Limits & considerations

1. LinkedIn API requires special query params characters (eg: `(`, `:` or `)`), and low-code automatically escapes them using `query params`.  
As auto-escaping disabling is not manageable via low-code, the workaround is to hard-code them in the request `path` directly.
2. `Incremental Sync` is not manageable via low-code due to LinkedIn API way to handle timerange via query param:
```
submittedAtTimeRange=(start:1711407600000,end:1711494000000)
```  
No workaround has been identified to manage this issue for now.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                           | Subject                                                 |
| :------ |:-----------|:-------------------------------------------------------|:--------------------------------------------------------|
| 0.1.0 | 2024-07-18 | [42101](https://github.com/airbytehq/airbyte/pull/42101) | Initial release of LinkedIn Leads connector for Airbyte |

</details>
