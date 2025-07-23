---
products: oss-enterprise, cloud-teams
---

# Single sign on (SSO)

import Tabs from "@theme/Tabs";
import TabItem from "@theme/TabItem";

Use Open ID Connect (OIDC) and generic OIDC to log into Airbyte using your Identity Provider (IdP), like Okta or Entra ID/Active Directory.

## Set up SSO

Administrators must set up SSO before your organization can use it. The steps differ slightly depending on which IdP you use and whether you're on the Cloud or Self-Managed version of Airbyte. To get started, choose your identity provider below.

```mdx-code-block
import DocCardList from '@theme/DocCardList';

<DocCardList />
```

## Log into Airbyte using SSO

<Tabs groupId="product">
<TabItem value="cloud" label="Cloud">

Once your contact at Airbyte informs you that you’re all set up, you can log into Airbyte using SSO. 

1. Visit [Airbyte Cloud](https://cloud.airbyte.com) and click **Continue with SSO**.

2. Specify your **Company identifier**, then click **Continue with SSO**. Airbyte forwards you to your identity provider's login page (for example, the Okta login page). Log into your work account. Your IdP forwards you back to Airbyte Cloud, which logs you in.

</TabItem>
<TabItem value="self-managed" label="Self-Managed">

1. Access your self-managed instance of Airbyte at the URL your organization has set up. Airbyte automatically forwards you to your identity provider's login page.

2. Log into your IdP. Your IdP forwards you back to Airbyte, which logs you in.

</TabItem>
</Tabs>

:::note
If you were already logged into your company’s IdP somewhere else, you might not see a login screen. Instead, Airbyte forwards you directly to Airbyte's logged-in area.
:::
