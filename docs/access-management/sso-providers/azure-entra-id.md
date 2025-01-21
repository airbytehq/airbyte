---
sidebar_label: Microsoft Entra ID
products: cloud-teams, oss-enterprise
---

import Tabs from "@theme/Tabs";
import TabItem from "@theme/TabItem";

# Setup Single Sign-On via Microsoft Entra ID

This page guides you through setting up [Single Sign-On](../sso.md) with Airbyte using **Microsoft Entra ID** (formerly known as **Azure ActiveDirectory**).

Airbyte will communicate with your Entra ID using OpenID Connect (OIDC).

<Tabs groupId="cloud-hosted">
<TabItem value="Cloud" label="Cloud">

## Creating an Entra ID app for Airbyte

:::info
The following steps need to be executed by an administrator of your company's Microsoft Entra ID account.
:::

You'll require to know your **Company Identifier** to create your application. You receive this
from your contact at Airbyte.

### Create application

You will need to create a new Entra ID application for Airbyte. Log into the [Azure Portal](https://portal.azure.com/) and search for the Entra ID service.

From the overview page of Entra ID, press **Add** > **App registration** on the top of the screen.

Specify any name you want (e.g. "Airbyte") and configure a **Redirect URI** of type **Web** with the following value:

```
https://cloud.airbyte.com/auth/realms/<your-company-identifier>/broker/default/endpoint
```

Hit **Register** to create the application.

### Create Client credentials

To create Client credentials for Airbyte to talk to your application head to **Certificates & Secrets** on the detail screen of your application and select the **Client secrets** tab.

Click **New client secret**, specify any Description you want and any expiry date you want.

:::tip
We recommend to chose an expiry date of at least 12 months. You'll need to pass in the new client secret every time the old one expires to continue being able to log in via Entra ID.
:::

Copy the **Value** (the Client Secret itself) immediately after creation. You won't be able to view this later on.

### Setup information needed

You'll need to pass your Airbyte contact the following information of the created application.

- **Client Secret**: as copied above
- **Application (client) ID**: You'll find this in the **Essentials** section on the **Overview** page of the application you created
- **OpenID Connect metadata document**: You'll find this in the **Endpoints** panel, that you can open from the top bar on the **Overview** page
- **Email Domain**: Users signing in from this domain will be required to sign in via SSO.

Once we've received this information from you, We'll setup SSO for you and let you know once it's ready to be used.

:::warning
For security purposes, existing [Applications](https://reference.airbyte.com/reference/authentication) used to access the Airbyte API that were created before enabling SSO **will be disabled** once the user that owns the Application signs in via SSO for the first time. After enabling SSO, please make sure to replace any Application secrets that were previously in use.
:::

</TabItem>
<TabItem value="Self-Managed" label="Self-Managed">

## Creating an Entra ID app for Airbyte

:::info
The following steps need to be executed by an administrator of your company's Azure Entra ID account.
:::

### Create application

You will need to create a new Entra ID application for Airbyte. Log into the [Azure Portal](https://portal.azure.com/) and search for the Entra ID service.

From the overview page of Entra ID, press **Add** > **App registration** on the top of the screen. The name you select is your app integration name. Once chosen, **choose who can use the application, typically set to "Accounts in this organization directory only" for specific access,** and configure a **Redirect URI** of type **Web** with the following value:

```
<your-airbyte-domain>/auth/realms/airbyte/broker/<app-integration-name>/endpoint
```

Hit **Register** to create the application.

### Create client credentials

To create client credentials for Airbyte to interface with your application, head to **Certificates & Secrets** on the detail screen of your application and select the **Client secrets** tab. Then:

1. Click **New client secret**, and enter the expiry date of your choosing. You'll need to pass in the new client secret every time the old one expires to continue being able to log in via Entra ID.
2. Copy the **Value** (the client secret itself) immediately after creation. You won't be able to view this later on.

:::caution
Depending on the default "Admin consent require' value for your organization you may need to manually provide Admin consent within the **API Permissions** menu. To do so click **API Permissions** and then click **Grant admin consent for Airbtyte** (see image below.)
:::

<img width="928" alt="Admin Consent Option" src="https://github.com/airbytehq/airbyte/assets/156025126/30818c10-de4f-4411-ba1d-8d82b74326fd" />

### Setup information needed

Once your Microsoft Entra ID app is set up, you're ready to deploy Airbyte Self-Managed Enterprise with SSO. Take note of the following configuration values, as you will need them to configure Airbyte to use your new Okta SSO app integration:

    * OpenID Connect metadata document: You'll find this in the list of endpoints found in the **Endpoints** panel, which you can open from the top bar of the **Overview** page. This will be used to populate the `Domain` field in your `airbyte.yml`.
    * App Integration Name: The name of the Entra ID application created in the first step.
    * Client ID: You'll find this in the **Essentials** section on the **Overview** page of the application you created.
    * Client Secret: The client secret you copied in the previous step.

Use this information to configure the auth details of your `airbyte.yml` for your Self-Managed Enterprise deployment. To learn more on deploying Self-Managed Enterprise, see our [implementation guide](/enterprise-setup/implementation-guide).

</TabItem>
</Tabs>
