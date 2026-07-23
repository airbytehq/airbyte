---
products: oss-enterprise, cloud
---

# Single sign on (SSO)

import Tabs from "@theme/Tabs";
import TabItem from "@theme/TabItem";
import CaptureHarFile from '../_partials/_capture-har-file.md';

Use Open ID Connect (OIDC) to log into Airbyte using an Identity Provider (IdP) like Okta or Entra ID/Active Directory.

## Set up single sign on

Administrators must set up SSO before your organization can use it. The steps differ slightly depending on which IdP you use and whether you're on the Cloud or Self-Managed version of Airbyte. To get started, choose your identity provider below.

```mdx-code-block
import DocCardList from '@theme/DocCardList';

<DocCardList />
```

## Log into Airbyte using single sign on

<Tabs groupId="product">
<TabItem value="cloud" label="Cloud">

1. Visit [Airbyte Cloud](https://cloud.airbyte.com) and click **Continue with SSO**.

2. Type your **Company identifier**, then click **Continue with SSO**. Airbyte forwards you to your identity provider's login page. 

3. Log into your work account. Your IdP forwards you back to Airbyte Cloud, which logs you in.

</TabItem>
<TabItem value="self-managed" label="Self-Managed">

1. Access your self-managed instance of Airbyte at the URL your organization has set up. Airbyte automatically forwards you to your identity provider's login page.

2. Log into your IdP. Your IdP forwards you back to Airbyte, which logs you in.

</TabItem>
</Tabs>

:::note
If you were already logged into your company’s IdP somewhere else, you might not see a login screen. In this case, Airbyte forwards you directly to Airbyte's logged-in area.
:::

## Troubleshooting

If you contact [Airbyte Support](https://support.airbyte.com/) about an SSO login problem, including a HAR file and the details of the relevant network requests helps Airbyte diagnose your issue and turn around a resolution faster.

### Capture a HAR file

<CaptureHarFile />

### Find the authentication requests

SSO login sends your browser through a series of redirects between Airbyte and your identity provider. Capturing these requests shows where the login flow breaks down.

1. Open developer tools and click the **Network** tab, following the steps above to capture requests.

2. Select **Preserve log** (**Persist Logs** in Firefox). This is important for SSO, because the login flow redirects across multiple pages and domains, and requests are otherwise cleared on each redirect.

3. Reproduce the problem by attempting to log in with SSO.

4. Look for requests to your identity provider (for example, Okta or Entra ID) and to Airbyte's authentication endpoints, and for any request that returns a `4xx` or `5xx` status.

5. Click a failing request and review the **Response** and **Preview** tabs for error messages, and the **Headers** tab for the request details.

6. Include these requests, along with the HAR file, in your support submission.
