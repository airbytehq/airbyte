---
sidebar_label: Entra ID
products: cloud-teams, oss-enterprise
---

import Tabs from "@theme/Tabs";
import TabItem from "@theme/TabItem";

# Set up single sign on using Entra ID

This guide shows you how to set up Microsoft Entra ID (formerly Azure ActiveDirectory) and Airbyte so your users can log into Airbyte using your organization's identity provider (IdP) using OpenID Connect (OIDC). 

## Overview

This guide is for administrators. It assumes you have:

- Basic knowledge of Entra ID, OIDC, and Airbyte
- The permissions to manage Entra ID in your organization
- The permissions to manage Airbyte in your organization

The exact process differs between the Cloud or Self-Managed versions of Airbyte. Steps for both are below.

## Cloud Teams with Entra ID OIDC

:::warning
For security purposes, Airbyte disables existing [applications](/platform/enterprise-setup/api-access-config) used to access the Airbyte API once the user who owns the application signs in with SSO for the first time. Replace any Application secrets that were previously in use to ensure your integrations don't break.
:::

Before you can proceed, you require your **Company Identifier** so you can properly fill in these values. Your contact at Airbyte gives this to you.

### Set up SSO in Airbyte for the first time

#### Create an application in Entra ID

Create a new [Entra ID application](https://learn.microsoft.com/en-us/entra/identity/enterprise-apps/what-is-application-management).

1. Log into the [Azure Portal](https://portal.azure.com/) and search for the Entra ID service.

2. From the Entra ID overview page, click **Add** > **App registration** at the top of the screen.

3. Specify any name you want (for example, "Airbyte").

4. Configure a **Redirect URI** with the type **Web** and the following value: `https://cloud.airbyte.com/auth/realms/<your-company-identifier>/broker/default/endpoint`

5. Click **Register** to create the application.

#### Create client credentials in Entra ID

Create client credentials so Airbyte can talk to your application.

1. On your application details page, click **Certificates & Secrets**.

2. Click the **Client secrets** tab.

3. Click **New client secret**. Specify any description you want and any expiry date you want.

    :::tip
    Choose an expiry date at least 12 months in the future, if you can. When a client secret expires, you need to give Airbyte the new one or people won't be able to log in.
    :::

4. Copy the **Value** (the client secret itself) immediately after you create it. You won't be able to view this later.

#### Configure SSO in Airbyte

1. In Airbyte, click **Settings**.

2. Under **Organization**, click **General**.

3. Click **Set up SSO**, then input the following information.

    - **Email domain**: The full email domain of users who sign in to Entra ID. For example, `airbyte.io`.

        :::note
      If you use multiple email domains, only enter one domain here. Contact Airbyte's [support team](https://support.airbyte.com) to have them add additional domains after you're done.
      :::

    - **Client ID**: Find this in the Essentials section of your Entra ID application's homepage.

    - **Client secret**: The client secret you created in the preceding section.

    - **Discovery URL**: Your OpenID Connect metadata endpoint. The format is similar to `https://login.microsoftonline.com/{tenant_id}/v2.0/.well-known/openid-configuration`.

    - **SSO subdomain**: Your company identifier, which users enter to access Airbyte.

      - It must be a unique.

      - It must be consistent with the company identifier you used in the redirect URI you defined in Entra ID.

      - It's often your organization name or domain. For example, `airbyte`.

4. Click **Save changes**.

5. Test SSO to make sure people can access Airbyte. **Stay logged in so you don't lock yourself out** and ask a colleague to complete the following steps.

    1. Sign out of Airbyte.

    2. On the Airbyte login page, click **Continue with SSO**, enter your company identifier, and click **Continue with SSO**. The Entra ID sign in page appears.

    3. Sign into Entra ID. Entra ID then forwards you back to Airbyte, which logs you in.

    :::note
    If you were already logged into your company’s IdP somewhere else, you might not see a login screen. In this case, Airbyte forwards you directly to Airbyte's logged-in area.
    :::

If you successfully set up SSO, but your users can't log into Airbyte, verify that they have access to the Airbyte application you created in Entra ID.

### Update or delete SSO configurations

To prevent a situation where you could lock yourself out of Airbyte, we require that you contact Airbyte's [support team](https://support.airbyte.com) if you need to change or remove SSO in your Cloud organization.

## Self-Managed Enterprise with Entra ID OIDC

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

Once your Microsoft Entra ID app is set up, you're ready to deploy Airbyte Self-Managed Enterprise with SSO. Take note of the following configuration values, as you will need them to configure Airbyte to use your new SSO app integration:

    * OpenID Connect metadata document: You'll find this in the list of endpoints found in the **Endpoints** panel, which you can open from the top bar of the **Overview** page. This will be used to populate the `Domain` field in your `airbyte.yml`.
    * App Integration Name: The name of the Entra ID application created in the first step.
    * Client ID: You'll find this in the **Essentials** section on the **Overview** page of the application you created.
    * Client Secret: The client secret you copied in the previous step.

Use this information to configure the auth details of your `airbyte.yml` for your Self-Managed Enterprise deployment. To learn more on deploying Self-Managed Enterprise, see our [implementation guide](/platform/enterprise-setup/implementation-guide).

## Self-Managed Enterprise with Entra ID Generic OIDC

To set up single sign on for Airbyte Self-Managed Enterprise, complete the following steps.

- [Create an Entra ID application for Airbyte](#sme-entra-id-app)
- [Create client credentials](#sme-credentials)
- [Update Airbyte's values.yaml file](#sme-update-values)
- [Redeploy Airbyte](#sme-deploy)

:::note
You can only use generic OIDC after you migrate to Helm chart V2.
<!-- [Helm chart V2](../../enterprise-setup/chart-v2-enterprise). -->
:::

### Create application {#sme-entra-id-app}

To start, you create a new Entra ID application for Airbyte.

1. Log into the [Azure Portal](https://portal.azure.com/), search for the Entra ID service, and go to the Entra ID overview page.

2. Click **Add** > **App registration**.

3. Fill out the Register an application form.

    - **Name**: Enter a descriptive integration name.

    - **Supported account types**: Choose "Accounts in this organizational directory only" unless you have a reason to choose a different one.

    - **Redirect URI**: Choose **Single-page application (SPA)** and enter the domain depends of your Airbyte installation location, but the URI should look similar to `https://airbyte.example.com`.

4. Click **Register**. You are taken to your application's overview page.

5. Click **Endpoints**.

6. Copy the URL for **OpenID Connect metadata document** and open it in a new tab. You need some of these values later, so set it aside for a moment.

### Create client credentials {#sme-credentials}

You need to complete several steps to properly authenticate.

#### Expose an API

1. Click **Manage** > **Expose an API** > **Add a scope**.

2. Click **Save and continue**.

3. Fill out the form.

    - **Who can consent?**: Set to **Admins and users**.

    - **Admin content display name**: Provide a name like "Airbyte access".

    - **Admin content description**: Provide a description like "Allow access to Airbyte".

    - **State**: Enabled.

    - Set other fields as you like.

4. Click **Add scope**.

5. Click **Add a client application**. Fill out the form to link your client application and your scope.

#### Make yourself an owner

1. Click **Manage** > **Owners** > **Add owners**.

2. Add yourself as an owner and click **Select**.

#### Grant API permissions

1. Click **Manage** > **API permissions** > **Add a permission**

2. Click **My APIs**.

3. Click your Airbyte application.

4. Grant your "Airbyte access" permission you created earlier.

5. **Delete** any **Microsoft Graph** permissions.

### Update Airbyte's values.yaml file {#sme-update-values}

Once you have an app integration for Airbyte, update the values.yaml file you use when you deploy Airbyte. This section is where you need information from the well-known endpoint you opened earlier.

Under `global`, add a new `auth` section and fill in the following data.

```yaml title="values.yaml"
global: 

  edition: "enterprise"
  airbyteUrl: "airbyte.example.com"

  enterprise:
    secretName: "airbyte-license"
    licenseKeySecretKey: "LICENSE_KEY"

  # Add this new auth section. See below for help populating these values.
  auth:
    identityProvider: 
      type: generic-oidc
      generic-oidc: 
        clientId: YOUR_CLIENT_ID
        audience: YOUR_AUDIENCE
        issuer: YOUR_ISSUER
        endpoints: 
          authorizationServerEndpoint: YOUR_AUTH_ENDPOINT
          jwksEndpoint: YOUR_JWKS_ENDPOINT
```
You collect these values from Microsoft in the locations shown below.
- `clientId`: In Entra ID, on your application page, use the **Application (client) ID**.

- `audience`: Same as `clientId`.

- `issuer`: In your well-known endpoint, use `issuer`.

- `authorizationServerEndpoint`: Same as `issuer`.

- `jwksEndpoint`: In your well-known endpoint, use `jwks_uri`.

### Redeploy Airbyte {#sme-deploy}

In your command-line tool, deploy Airbyte using your updated values file.

```bash
helm upgrade airbyte-enterprise airbyte-v2/airbyte \
  --namespace airbyte-v2 \       # Target Kubernetes namespace
  --values ./values.yaml \       # Custom configuration values
  --version 2.0.3 \              # Helm chart version to use
  --set global.image.tag=1.7.0   # Airbyte version to use
```
