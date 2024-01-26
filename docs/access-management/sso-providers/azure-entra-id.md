---
sidebar_label: Azure Entra ID
products: cloud-teams
---

import Tabs from "@theme/Tabs";
import TabItem from "@theme/TabItem";

# Setup Single Sign-On via Azure Entra ID

This page guides you through setting up [Single Sign-On](../sso.md) with Airbyte using **Microsoft Azure Entra ID** (formerly known as **Azure Active Directory**).

Airbyte will communicate with your Entra ID using OpenID Connect (OIDC).

## Creating an Entra ID app for Airbyte

:::info
The following steps need to be executed by an administrator of your company's Azure Entra ID account.
:::

You'll require to know your **Company Identifier** to create your application. You receive this
from your contact at Airbyte.

### Create application

You will need to create a new Entra ID application for Airbyte. Log into the [Azure Portal](https://portal.azure.com/) and search for the Entra ID service.

On the Overview of Entra ID press **Add** > **App registration** on the top of the screen.

Specify any name you want (e.g. "Airbyte") and configure a **Redirect URI** of type **Web** with the following value:

```
https://cloud.airbyte.com/auth/realms/<your-company-identifier>/broker/default/endpoint
```

Hit **Register** to create the application.

### Create Client credentials

To create Client credentials for Airbyte to talk to your application head to **Certificates & Secrets** on the detail screen of your application and select the **Client secrets** tab.

Click **New client secret**, specify any Description you want and any Expire date you want. 

:::tip
We recommend to chose an expiry date of at least 12 months. You'll need to pass the new Client Secret to use every time the old one expires, to continue being able to log in via Entra ID.
:::

Copy the **Value** (the Client Secret itself) immediately after creation. You won't be able to view this later on again.

### Setup information needed

You'll need to pass your Airbyte contact the following information of the created application.

* **Client Secret**: as copied above
* **Application (client) ID**: You'll find this in the **Essentials** section on the **Overview** page of the application you created
* **OpenID Connect metadata document**: You'll find this in the **Endpoints** panel, that you can open from the top bar on the **Overview** page

Once we've received this information from you, We'll setup SSO for you and let you know once it's ready to be used.
