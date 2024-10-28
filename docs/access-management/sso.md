---
products: oss-enterprise, cloud-teams
---

# Single Sign-On (SSO)

import Tabs from "@theme/Tabs";
import TabItem from "@theme/TabItem";

Single Sign-On (SSO) allows you to enable logging into Airbyte using your existing Identity Provider (IdP) like Okta or Active Directory.

SSO is available in Airbyte Enterprise and on Cloud with the Teams add-on. [Talk to us](https://airbyte.com/company/talk-to-sales) if you are interested in setting up SSO for your organization.

## Set up

You can find setup explanations for all our supported Identity Providers on the following subpages:

```mdx-code-block
import DocCardList from '@theme/DocCardList';

<DocCardList />
```

## Logging in

<Tabs groupId="cloud-hosted">
  <TabItem value="cloud" label="Cloud">
    Once we inform you that you’re all set up, you can log into Airbyte using SSO by visiting [cloud.airbyte.com/sso](https://cloud.airbyte.com/sso) or select the **Continue with SSO** option on the login screen.
    
    Specify your _company identifier_ and hit “Continue with SSO”. You’ll be forwarded to your IdP's login page (e.g. Okta login page). Log into your work account and you’ll be forwarded back to Airbyte Cloud and be logged in.
    
    *Note:* you were already logged into your company’s Okta account you might not see any login screen and directly get forwarded back to Airbyte Cloud.
  </TabItem>
  <TabItem value="self-managed" label="Self-Managed">
    Accessing your self hosted Airbyte will automatically forward you to your IdP's login page (e.g. Okta login page). Log into your work account and you’ll be forwarded back to your Airbyte and be logged in.
  </TabItem>
</Tabs>
